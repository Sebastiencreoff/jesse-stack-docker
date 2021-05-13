#! /usr/bin/env python

import os

from binance_f import RequestClient
from binance_f.model.constant import *

import jesse.helpers as jh
import jesse.services.selectors as selectors
from jesse.enums import order_roles, order_types, sides
from jesse.exchanges.exchange import Exchange
from jesse.models import Order
from jesse.store import store


class BaseBinance(Exchange):
    """"""

    def __init__(self, api_key: str, name: str, secret_key: str, dev: bool = True):
        super().__init__()

        self.name = name

        kwargs = {
            "api_key": api_key,
            "secret_key": secret_key,
        }
        if dev:
            kwargs["url"] = "https://testnet.binancefuture.com"
        self.request_client = RequestClient(**kwargs)

        # Change to hedge mode.
        try:
            self.request_client.change_position_mode(dualSidePosition=True)
        except Exception as exc:
            if "No need to change position side" not in exc.error_message:
                raise exc

        self.init_symbols = []

    def initial_leverage(self, symbol):

        if symbol not in self.init_symbols:
            exchange = selectors.get_exchange(self.name)
            self.request_client.change_initial_leverage(
                symbol, exchange.futures_leverage
            )
            self.init_symbols.append(symbol)

    def order_side(self, side):
        return OrderSide.BUY if side == sides.BUY else OrderSide.SELL

    def prepare_qty(self, qty, side):
        return str(abs(jh.prepare_qty(qty, side)))

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
        breakpoint()

        self.initial_leverage(symbol)
        quantity = self.prepare_qty(qty, side)

        position_side = PositionSide.INVALID
        order_side = self.order_side(side)
        if role in [order_roles.OPEN_POSITION, order_roles.INCREASE_POSITION]:
            position_side = (
                PositionSide.LONG if side == sides.BUY else PositionSide.SHORT
            )
        if role in [order_roles.CLOSE_POSITION, order_roles.REDUCE_POSITION]:
            position_side = (
                PositionSide.SHORT if side == sides.BUY else PositionSide.LONG
            )

        client_order_id = jh.generate_unique_id()
        response = self.request_client.post_order(
            symbol,
            order_side,
            OrderType.MARKET,
            newClientOrderId=client_order_id,
            positionSide=position_side,
            quantity=quantity,
        )

        order = Order(
            {
                "id": client_order_id,
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
        order.execute()

        store.orders.add_order(order)

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
        breakpoint()
        # Set to str to
        quantity = self.prepare_qty(qty, side)

        if role in [order_roles.OPEN_POSITION, order_roles.INCREASE_POSITION]:
            position_side = (
                PositionSide.LONG if side == sides.BUY else PositionSide.SHORT
            )
        if role in [order_roles.CLOSE_POSITION, order_roles.REDUCE_POSITION]:
            position_side = (
                PositionSide.SHORT if side == sides.BUY else PositionSide.LONG
            )

        client_order_id = jh.generate_unique_id()
        response = self.request_client.post_order(
            symbol,
            self.order_side(side),
            OrderType.LIMIT,
            newClientOrderId=client_order_id,
            positionSide=position_side,
            price=price,
            quantity=quantity,
            timeInForce=TimeInForce.GTC,
        )

        order = Order(
            {
                "id": client_order_id,
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

        breakpoint()
        quantity = self.prepare_qty(qty, side)

        if role in [order_roles.OPEN_POSITION, order_roles.INCREASE_POSITION]:
            position_side = (
                PositionSide.LONG if side == sides.BUY else PositionSide.SHORT
            )
        if role in [order_roles.CLOSE_POSITION, order_roles.REDUCE_POSITION]:
            position_side = (
                PositionSide.SHORT if side == sides.BUY else PositionSide.LONG
            )

        client_order_id = jh.generate_unique_id()

        if side == sides.BUY:
            stop_price = price
            price = price * 0.99
        else:
            stop_price = price * 1.01

        response = self.request_client.post_order(
            symbol,
            self.order_side(side),
            OrderType.STOP,
            newClientOrderId=client_order_id,
            positionSide=position_side,
            price=str(price),
            quantity=quantity,
            stopPrice=str(stop_price),
            timeInForce=TimeInForce.GTC,
        )

        order = Order(
            {
                "id": client_order_id,
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

        breakpoint()
        self.request_client.cancel_all_orders(symbol)
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
        breakpoint()
        self.request_client.cancel_order(symbol, origClientOrderId=order_id)
        store.orders.get_order_by_id(self.name, symbol, order_id).cancel()

    def get_exec_inst(self, flags):
        """

        :param flags:
        :return:
        """
        if flags:
            return flags[0]
        return None
