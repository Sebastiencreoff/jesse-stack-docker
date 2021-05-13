#! /usr/bin/env python

import os

from binance_f import RequestClient

from .basebinance import BaseBinance


class Binance(BaseBinance):
    """"""

    def __init__(self, name: str = "Binance"):
        self.exchange_id = "1"

        self.api_key = os.environ.get("BINANCE_API_KEY")
        self.secret_key = os.environ.get("BINANCE_SECRET_KEY")

        super().__init__(self.api_key, name, self.secret_key, dev=False)

    @staticmethod
    def exchange_information():
        response = RequestClient().get_exchange_information()
        return {
            # done for testnet
            symbol.symbol: {
                "price_precision": symbol.pricePrecision,
                "qty_precision": symbol.quantityPrecision,
            }
            for symbol in response.symbols
        }
