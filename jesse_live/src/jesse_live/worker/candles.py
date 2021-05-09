#! /usr/bin/env python

from typing import Dict, Union

import arrow
import numpy as np

from jesse.enums import timeframes
from jesse.modes.import_candles_mode.drivers import drivers
from jesse.modes.import_candles_mode.drivers.interface import CandleExchange


class CandleInput:
    def __init__(self, exchange, symbol, timeframe: timeframes):

        self.symbol = symbol
        self.timeframe = timeframe
        try:
            self.driver: CandleExchange = drivers[exchange.title()]()
        except KeyError:
            raise ValueError(f'{exchange} is not a supported exchange')

    def preload_candles(
        self, candles_number
    ) -> Dict[str, Dict[str, Union[str, np.ndarray]]]:

        # Get candles in 1 minute.
        candles = self.driver.fetch(
            self.symbol, arrow.utcnow().int_timestamp * 1000 - candles_number * 60000
        )

        print(candles)

        # # download candles for the duration of the backtest
        # candles = {}
        # for c in config['app']['considering_candles']:
        #     exchange, symbol = c[0], c[1]

        #     key = jh.key(exchange, symbol)

        #     cache_key = f"{start_date_str}-{finish_date_str}-{key}"
        #     cached_value = cache.get_value(cache_key)
        #     # if cache exists
        #     if cached_value:
        #         candles_tuple = cached_value
        #     # not cached, get and cache for later calls in the next 5 minutes
        #     else:
        #         # fetch from database
        #         candles_tuple = Candle.select(
        #             Candle.timestamp, Candle.open, Candle.close, Candle.high, Candle.low,
        #             Candle.volume
        #         ).where(
        #             Candle.timestamp.between(start_date, finish_date),
        #             Candle.exchange == exchange,
        #             Candle.symbol == symbol
        #         ).order_by(Candle.timestamp.asc()).tuples()

        #     # validate that there are enough candles for selected period
        #     required_candles_count = (finish_date - start_date) / 60_000
        #     if len(candles_tuple) == 0 or candles_tuple[-1][0] != finish_date or candles_tuple[0][0] != start_date:
        #         raise exceptions.CandleNotFoundInDatabase(
        #             f'Not enough candles for {symbol}. Try running "jesse import-candles"')
        #     elif len(candles_tuple) != required_candles_count + 1:
        #         raise exceptions.CandleNotFoundInDatabase(f'There are missing candles between {start_date_str} => {finish_date_str}')

        #     # cache it for near future calls
        #     cache.set_value(cache_key, tuple(candles_tuple), expire_seconds=60 * 60 * 24 * 7)

        #     candles[key] = {
        #         'exchange': exchange,
        #         'symbol': symbol,
        #         'candles': np.array(candles_tuple)
        #     }

        return candles

    def next_candle(self):

        return self.driver.fetch(arrow.utcnow().int_timestamp * 1000 - 1 * 60000)
