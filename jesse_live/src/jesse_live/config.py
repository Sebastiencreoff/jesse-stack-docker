#!/usr/bin/env python

from typing import Dict

from jesse_live.drivers import Binance, TestNetBinance

CONFIG_LIVE = {
    # these values are related to the user's environment
    "env": {
        "notifications": {
            "enable_notifications": False,
            "events": {
                "errors": True,
                # Orders notifications
                "cancelled_orders": True,
                "executed_orders": True,
                "submitted_orders": True,
                "updated_position": True,
            },
            "general_notifier": {
                "telegram_bot_token": "",
                "telegram_chat_IDs": "",
            },
            "error_notifier": {
                "telegram_bot_token": "",
                "telegram_chat_IDs": "",
            },
        }
    },
    # These values are just placeholders used by Jesse at runtime
    "app": {
        # dict of registered live trade drivers
        "live_drivers": {"Binance": Binance, "Testnet Binance Futures": TestNetBinance},
    },
}


def init(config: Dict[str, any], config_live: Dict[str, any]):

    import jesse.services.selectors as selectors
    from jesse.services.api import api
    from jesse.store import install_routes

    # Update live exchange
    config["app"]["live_drivers"] = CONFIG_LIVE["app"]["live_drivers"]

    # Update notifications
    config["env"]["notifications"] = CONFIG_LIVE["env"]["notifications"]

    for key, class_ in config["app"]["live_drivers"].items():
        exchange = selectors.get_exchange(key)
        if exchange:
            exchange.vars["precisions"] = class_()._get_precisions()

    install_routes()
    api.initiate_drivers()

    # Init exchange
