import datetime
import time
from typing import Dict, Union

import arrow
import click
import numpy as np

import jesse.helpers as jh
import jesse.services.metrics as stats
import jesse.services.selectors as selectors
import jesse.services.table as table
from jesse import exceptions
from jesse.config import config
from jesse.enums import timeframes
from jesse.models import Candle
from jesse.modes.import_candles_mode.drivers import drivers
from jesse.modes.utils import save_daily_portfolio_balance
from jesse.routes import router
from jesse.services import charts, report
from jesse.services.cache import cache
from jesse.services.candle import (
    candle_includes_price,
    generate_candle_from_one_minutes,
    print_candle,
    split_candle,
)
from jesse.services.validators import validate_routes
from jesse.store import store

RUNNING = True


def terminate():
    global RUNNING
    RUNNING = False


def run(dev: bool, chart: bool = False) -> None:
    # clear the screen
    if not jh.should_execute_silently():
        click.clear()

    config['app']['is_unit_testing'] = dev
    # validate routes
    validate_routes(router)

    # initiate candle store
    store.candles.init_storage(5000)

    print('preloading candles...')

    candles = preload_candles()
    click.clear()

    if not jh.should_execute_silently():
        # print candles table
        key = f"{config['app']['considering_candles'][0][0]}-{config['app']['considering_candles'][0][1]}"
        table.key_value(
            stats.candles(candles[key]['candles']),
            'candles',
            alignments=('left', 'right'),
        )
        print('\n')

        # print routes table
        table.multi_value(stats.routes(router.routes))
        print('\n')

        # print guidance for debugging candles
        if jh.is_debuggable('trading_candles') or jh.is_debuggable(
            'shorter_period_candles'
        ):
            print(
                '     Symbol  |     timestamp    | open | close | high | low | volume'
            )

    # run backtest simulation
    live(candles, dev)

    if not jh.should_execute_silently():
        # print trades metrics
        if store.completed_trades.count > 0:

            change = []
            # calcualte market change
            for e in router.routes:
                if e.strategy is None:
                    return

                first = (
                    Candle.select(Candle.close)
                    .where(
                        Candle.timestamp == jh.date_to_timestamp(start_date),
                        Candle.exchange == e.exchange,
                        Candle.symbol == e.symbol,
                    )
                    .first()
                )
                last = (
                    Candle.select(Candle.close)
                    .where(
                        Candle.timestamp == jh.date_to_timestamp(finish_date) - 60000,
                        Candle.exchange == e.exchange,
                        Candle.symbol == e.symbol,
                    )
                    .first()
                )

                change.append(((last.close - first.close) / first.close) * 100.0)

            data = report.portfolio_metrics()
            data.append(['Market Change', f"{str(round(np.average(change), 2))}%"])
            print('\n')
            table.key_value(data, 'Metrics', alignments=('left', 'right'))
            print('\n')

            if chart:
                charts.portfolio_vs_asset_returns()


def fetch_candles(exchange, symbol, start_date: int) -> np.ndarray:
    try:
        breakpoint()
        driver = drivers[exchange.title()]()
        response = driver.fetch(symbol, start_date * 1000)
        # Response of Binance is down in timestamp desc.
        # Transform from {'symbol': 'DOGE-USDT', 'exchange': 'Binance', 'timestamp': 1619880780000, 'open': 0.35787, 'close': 0.35823, 'high': 0.3585, 'low': 0.3578, 'volume': 1264391.4}
        # to (timestamp, open, close, high, low, volume)
        return np.array(
            [
                (
                    item['timestamp'],
                    item['open'],
                    item['close'],
                    item['high'],
                    item['low'],
                    item['volume'],
                )
                for item in response
            ]
        )
    except KeyError:
        raise ValueError(f'{exchange} is not a supported exchange')


def preload_candles() -> Dict[str, Dict[str, Union[str, np.ndarray]]]:

    finish_date = arrow.utcnow().int_timestamp * 1000 - 60000
    start_date = (
        arrow.utcnow().int_timestamp - config['env']['data']['warmup_candles_num'] * 60
    )

    # download candles for the duration of the backtest
    candles = {}
    for c in config['app']['considering_candles']:
        exchange, symbol = c[0], c[1]

        key = jh.key(exchange, symbol)

        cache_key = f"{start_date}-{finish_date}-{key}"
        cached_value = cache.get_value(cache_key)
        # if cache exists
        if cached_value:
            candles_tuple = cached_value
        # not cached, get and cache for later calls in the next 5 minutes
        else:
            candles_tuple = fetch_candles(exchange, symbol, start_date)

        # cache it for near future calls
        cache.set_value(
            cache_key, tuple(candles_tuple), expire_seconds=60 * 60 * 24 * 7
        )

        candles[key] = {
            'exchange': exchange,
            'symbol': symbol,
            'candles': np.array(candles_tuple),
        }

    return candles


def wait_for_next_candle(next_time: arrow.Arrow):

    while RUNNING:
        if arrow.utcnow().int_timestamp > next_time.int_timestamp:
            return
        else:
            time.sleep(10)


def live(
    candles: Dict[str, Dict[str, Union[str, np.ndarray]]], dev: bool = False
) -> None:

    key = f"{config['app']['considering_candles'][0][0]}-{config['app']['considering_candles'][0][1]}"
    first_candles_set = candles[key]['candles']

    store.app.starting_time = arrow.get(first_candles_set[-1][0])
    store.app.time = arrow.get(first_candles_set[-1][0])

    # initiate strategies
    for r in router.routes:
        StrategyClass = jh.get_strategy_class(r.strategy_name)

        try:
            r.strategy = StrategyClass()
        except TypeError:
            raise exceptions.InvalidStrategy(
                "Looks like the structure of your strategy directory is incorrect. Make sure to include the strategy INSIDE the __init__.py file."
                "\nIf you need working examples, check out: https://github.com/jesse-ai/example-strategies"
            )
        except:
            raise

        r.strategy.name = r.strategy_name
        r.strategy.exchange = r.exchange
        r.strategy.symbol = r.symbol
        r.strategy.timeframe = r.timeframe

        # init few objects that couldn't be initiated in Strategy __init__
        # it also injects hyperparameters into self.hp in case the route does not uses any DNAs
        r.strategy._init_objects()

        selectors.get_position(r.exchange, r.symbol).strategy = r.strategy

    # add initial balance
    save_daily_portfolio_balance()

    print('Executing live trading...')

    while RUNNING:
        # update time

        store.app.time = store.app.time.shift(minutes=1)

        wait_for_next_candle(store.app.time)
        minute_count = datetime.datetime.utcnow().minute

        # now that all new generated candles are ready, execute
        for r in router.routes:
            symbol_key = jh.key(r.exchange, r.symbol)
            short_candles = fetch_candles(
                r.exchange, r.symbol, store.app.time.int_timestamp
            )
            if len(short_candles):
                short_candles[0] = _get_fixed_jumped_candle(
                    candles[symbol_key]['candles'][0], short_candles[0]
                )
                for candle in short_candles:
                    store.candles.add_candle(
                        candle,
                        r.exchange,
                        r.symbol,
                        '1m',
                        with_execution=False,
                        with_generation=False,
                    )

            count = jh.timeframe_to_one_minutes(r.timeframe)
            # # 1m timeframe
            if r.timeframe == timeframes.MINUTE_1:
                # print candle
                if jh.is_debuggable('trading_candles'):
                    print_candle(
                        store.candles.get_current_candle(
                            r.exchange, r.symbol, r.timeframe
                        ),
                        False,
                        r.symbol,
                    )
                r.strategy._execute()
            elif (minute_count + 1) % count == 0:
                current_candles = store.candles.get_candles(
                    r.exchange, r.symbol, timeframes.MINUTE_1
                )

                if len(candles) >= count:
                    generated_candle = generate_candle_from_one_minutes(
                        r.timeframe, current_candles[-count:]
                    )
                    store.candles.add_candle(
                        generated_candle,
                        r.exchange,
                        r.symbol,
                        r.timeframe,
                        with_execution=False,
                        with_generation=False,
                    )

                    # print candle
                    if jh.is_debuggable('trading_candles'):
                        print_candle(
                            store.candles.get_current_candle(
                                r.exchange, r.symbol, r.timeframe
                            ),
                            False,
                            r.symbol,
                        )
                    r.strategy._execute()

        # now check to see if there's any MARKET orders waiting to be executed
        store.orders.execute_pending_market_orders()

        if minute_count == 0:
            save_daily_portfolio_balance()

        # now check to see if there's any MARKET orders waiting to be executed
        store.orders.execute_pending_market_orders()

    if not jh.should_execute_silently():
        if jh.is_debuggable('trading_candles') or jh.is_debuggable(
            'shorter_period_candles'
        ):
            print('\n')

    for r in router.routes:
        r.strategy._terminate()
        store.orders.execute_pending_market_orders()

    # now that backtest is finished, add finishing balance
    save_daily_portfolio_balance()


def _get_fixed_jumped_candle(
    previous_candle: np.ndarray, candle: np.ndarray
) -> np.ndarray:
    """
    A little workaround for the times that the price has jumped and the opening
    price of the current candle is not equal to the previous candle's close!

    :param previous_candle: np.ndarray
    :param candle: np.ndarray
    """
    if previous_candle[2] < candle[1]:
        candle[1] = previous_candle[2]
        candle[4] = min(previous_candle[2], candle[4])
    elif previous_candle[2] > candle[1]:
        candle[1] = previous_candle[2]
        candle[3] = max(previous_candle[2], candle[3])

    return candle


def _simulate_price_change_effect(
    real_candle: np.ndarray, exchange: str, symbol: str
) -> None:
    orders = store.orders.get_orders(exchange, symbol)

    current_temp_candle = real_candle.copy()
    executed_order = False

    while True:
        if len(orders) == 0:
            executed_order = False
        else:
            for index, order in enumerate(orders):
                if index == len(orders) - 1 and not order.is_active:
                    executed_order = False

                if not order.is_active:
                    continue

                if candle_includes_price(current_temp_candle, order.price):
                    storable_temp_candle, current_temp_candle = split_candle(
                        current_temp_candle, order.price
                    )
                    store.candles.add_candle(
                        storable_temp_candle,
                        exchange,
                        symbol,
                        '1m',
                        with_execution=False,
                        with_generation=False,
                    )
                    p = selectors.get_position(exchange, symbol)
                    p.current_price = storable_temp_candle[2]

                    executed_order = True

                    order.execute()

                    # break from the for loop, we'll try again inside the while
                    # loop with the new current_temp_candle
                    break
                else:
                    executed_order = False

        if not executed_order:
            # add/update the real_candle to the store so we can move on
            store.candles.add_candle(
                real_candle,
                exchange,
                symbol,
                '1m',
                with_execution=False,
                with_generation=False,
            )
            p = selectors.get_position(exchange, symbol)
            if p:
                p.current_price = real_candle[2]
            break
