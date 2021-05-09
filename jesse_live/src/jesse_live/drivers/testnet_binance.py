#! /usr/bin/env python

from binance_d import RequestClient
from binance_d.model.constant import *

from .binance import Binance


class TestNetBinance(Binance):
    """"""

    def __init__(self, name="Testnet Binance"):
        super().__init__()
        self.name = name
        self.exchange_id = '2'

        # self.api_key = os.environ['Binance_api_key'].strip()
        # self.secret_key = os.environ['Binance_secret_key'].strip()

        breakpoint()
        self.api_key = (
            "6073177a1ae8bcc44388ef8050451bbed97bc2fda71948c4e83915a6b9a504e3"
        )
        self.secret_key = (
            "f04d0a4b86e11ff050b0ed103c40372998c3cdec4a85e4f26a5b722d02bc1975"
        )
        self.request_client = RequestClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            url="https://testnet.binancefuture.com",
        )

    @staticmethod
    def exchange_information():
        response = RequestClient().get_exchange_information()
        return {
            # done for testnet
            symbol.symbol.replace('_PERP', 'T'): {
                'price_precision': symbol.pricePrecision,
                'qty_precision': symbol.quantityPrecision,
            }
            for symbol in response.symbols
        }
