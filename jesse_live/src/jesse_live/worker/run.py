#! /usr/bin/env python
import arrow
import time

from jesse.routes import router
from jesse.store import store
from jesse.services.validators import validate_routes

from jesse_live import config, utils
from .candles import CandleInput

RUNNING = True

def terminate():
    global RUNNING
    RUNNING = False

def wait_for_next_candle(timeframe):

    next_time =  arrow.utcnow().timestamp
    next_time.shift(minutes=utils.timeframes_to_minutes(timeframe))
    next_time.seconds = 0
    next_time.miliseconds = 0

    while RUNNING:
        if arrow.utcnow().timestamp > next_time.timestamp:
            return
        else:
            time.sleep(10)

def run(name:str, exchange: str, symbol:str, timeframe:str, dev=False):

    # validate routes
    validate_routes(router)

    # initiate candle store
    store.candles.init_storage(5000)

    breakpoint()
    candles = []
    # load historical candles
    print('preloading candles...')

    candle_service = CandleInput(exchange, symbol, timeframe)
    candle_service.preload_candles(config.config['env']['data']['warmup_candles_num'])

    while RUNNING:

        candle = candle_service.next_candle()
        # # print guidance for debugging candles
        # if jh.is_debuggable('trading_candles') or jh.is_debuggable('shorter_period_candles'):
        #     print('     Symbol  |     timestamp    | open | close | high | low | volume')

        # Wait for the next candle
        wait_for_next_candle()


