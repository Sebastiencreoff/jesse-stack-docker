#! /usr/bin/env python

import os

from binance_f import RequestClient

import jesse.helpers as jh
from jesse.enums import order_types
from jesse.exchanges.exchange import Exchange
from jesse.models import Order
from jesse.store import store


class Binance(Exchange):
    """"""

    def __init__(self, name="Binance"):
        super().__init__()
        self.name = name
        self.exchange_id = jh.generate_unique_id()

        self.request_client = RequestClient()

    @staticmethod
    def exchange_information():
        response = RequestClient().get_exchange_information()
        return {
            symbol.symbol: {
                'price_precision': symbol.pricePrecision,
                'qty_precision': symbol.quantityPrecision,
            }
            for symbol in response.symbols
        }

    def market_order(self, symbol, qty, current_price, side, role, flags):
        """

        :param symbol:
        :param qty:
        :param current_price:
        :param side:
        :param role:
        :param flags:
        :return:
        """
        order = Order(
            {
                "id": jh.generate_unique_id(),
                "symbol": symbol,
                "exchange": self.name,
                "exchange_id": self.exchange_id,
                "side": side,
                "type": order_types.MARKET,
                "flag": self.get_exec_inst(flags),
                "qty": jh.prepare_qty(qty, side),
                "price": current_price,
                "role": role,
            }
        )

        store.orders.add_order(order)

        store.orders.to_execute.append(order)

        return order

    def limit_order(self, symbol, qty, price, side, role, flags):
        """

        :param symbol:
        :param qty:
        :param price:
        :param side:
        :param role:
        :param flags:
        :return:
        """
        order = Order(
            {
                "id": jh.generate_unique_id(),
                "symbol": symbol,
                "exchange": self.name,
                "exchange_id": self.exchange_id,
                "side": side,
                "type": order_types.LIMIT,
                "flag": self.get_exec_inst(flags),
                "qty": jh.prepare_qty(qty, side),
                "price": price,
                "role": role,
            }
        )

        store.orders.add_order(order)

        return order

    def stop_order(self, symbol, qty, price, side, role, flags):
        """

        :param symbol:
        :param qty:
        :param price:
        :param side:
        :param role:
        :param flags:
        :return:
        """
        order = Order(
            {
                "id": jh.generate_unique_id(),
                "symbol": symbol,
                "exchange": self.name,
                "exchange_id": self.exchange_id,
                "side": side,
                "type": order_types.STOP,
                "flag": self.get_exec_inst(flags),
                "qty": jh.prepare_qty(qty, side),
                "price": price,
                "role": role,
            }
        )

        store.orders.add_order(order)

        return order

    def cancel_all_orders(self, symbol):
        """

        :param symbol:
        """
        orders = filter(lambda o: o.is_new, store.orders.get_orders(self.name, symbol))

        for o in orders:
            o.cancel()

        if not jh.is_unit_testing():
            store.orders.storage[f"{self.name}-{symbol}"].clear()

    def cancel_order(self, symbol, order_id):
        """

        :param symbol:
        :param order_id:
        """
        store.orders.get_order_by_id(self.name, symbol, order_id).cancel()

    def get_exec_inst(self, flags):
        """

        :param flags:
        :return:
        """
        if flags:
            return flags[0]
        return None
