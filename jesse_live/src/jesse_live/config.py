#!/usr/bin/env python

from typing import Dict

from jesse_live.drivers import Binance

CONFIG_LIVE = {
    # these values are related to the user's environment
    'env': {
        'databases': {
            'postgres_host': '127.0.0.1',
            'postgres_name': 'jesse_db',
            'postgres_port': 5432,
            'postgres_username': 'jesse_user',
            'postgres_password': 'password',
        },
        'caching': {'driver': 'pickle'},
        'logging': {
            'order_submission': True,
            'order_cancellation': True,
            'order_execution': True,
            'position_opened': True,
            'position_increased': True,
            'position_reduced': True,
            'position_closed': True,
            'shorter_period_candles': False,
            'trading_candles': True,
            'balance_update': True,
        },
        'exchanges': {
            # https://www.binance.com
            'Binance': {
                'fee': 0.001,
                # backtest mode only: accepted are 'spot' and 'futures'
                'type': 'futures',
                # futures mode only
                'settlement_currency': 'USDT',
                # accepted values are: 'cross' and 'isolated'
                'futures_leverage_mode': 'cross',
                # 1x, 2x, 10x, 50x, etc. Enter as integers
                'futures_leverage': 1,
                'assets': [
                    {'asset': 'USDT', 'balance': 10_000},
                    {'asset': 'BTC', 'balance': 0},
                ],
            },
            # https://www.binance.com
            'Binance Futures': {
                'fee': 0.0004,
                # backtest mode only: accepted are 'spot' and 'futures'
                'type': 'futures',
                # futures mode only
                'settlement_currency': 'USDT',
                # accepted values are: 'cross' and 'isolated'
                'futures_leverage_mode': 'cross',
                # 1x, 2x, 10x, 50x, etc. Enter as integers
                'futures_leverage': 1,
                'assets': [
                    {'asset': 'USDT', 'balance': 10_000},
                ],
            },
        },
        # changes the metrics output of the backtest
        'metrics': {
            'sharpe_ratio': True,
            'calmar_ratio': False,
            'sortino_ratio': False,
            'omega_ratio': False,
            'winning_streak': False,
            'losing_streak': False,
            'largest_losing_trade': False,
            'largest_winning_trade': False,
            'total_winning_trades': False,
            'total_losing_trades': False,
        },
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Data
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #
        # Below configurations are related to the data
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        'data': {
            # The minimum number of warmup candles that is loaded before each session.
            'warmup_candles_num': 240,
        },
    },
    # These values are just placeholders used by Jesse at runtime
    'app': {
        # dict of registered live trade drivers
        'live_drivers': {'Binance': Binance},
    },
}


def init(config: Dict[str, any], config_live: Dict[str, any]):

    import jesse.services.selectors as selectors
    from jesse.services.api import api
    from jesse.store import install_routes

    # Update live exchange
    config['app']['live_drivers'] = CONFIG_LIVE['app']['live_drivers']

    for key, class_ in config['app']['live_drivers'].items():
        exchange = selectors.get_exchange(key)
        exchange.vars['precisions'] = class_.exchange_information()

    install_routes()
    api.initiate_drivers()

    # Init exchange
