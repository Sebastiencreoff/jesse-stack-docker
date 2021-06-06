#! /usr/bin/env python

from binance_f import RequestClient

from .basebinance import BaseBinance


class TestNetBinance(BaseBinance):
    """"""

    def __init__(self, name="Testnet Binance Futures"):

        self.exchange_id = "2"

        self.api_key = (
            "6073177a1ae8bcc44388ef8050451bbed97bc2fda71948c4e83915a6b9a504e3"
        )
        self.secret_key = (
            "f04d0a4b86e11ff050b0ed103c40372998c3cdec4a85e4f26a5b722d02bc1975"
        )
        super().__init__(self.api_key, name, self.secret_key, dev=True)

    def _get_precisions(self):

        response = RequestClient().get_exchange_information()
        return {
            # done for testnet
            symbol.symbol.replace("_PERP", "T").replace("USD", "-USD"): {
                "price_precision": symbol.pricePrecision,
                "qty_precision": symbol.quantityPrecision,
            }
            for symbol in response.symbols
        }
