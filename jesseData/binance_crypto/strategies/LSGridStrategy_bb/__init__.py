import jesse.indicators as ta
from jesse import utils
from jesse.strategies import Strategy, cached

from .indicators import kdj

TAKE_PROFIT_PERCENT = 0.05
STOP_LOSS_PERCENT = 0.05
UPDATE_PERCENT = 0.02


class LSGridStrategy(Strategy):
    def should_long(self) -> bool:
        if self.bullish:
            # if close is lower than 10% of the lowerband
            if 0 < (self.close / self.bb.lowerband) * 100 - 100 < 10:
                return True

        return False

    def should_short(self) -> bool:
        if self.bearish:
            # if close is lower than 10% of the lowerband
            if 0 < (self.bb.upperband / self.close) * 100 - 100 < 10:
                return True

        return False

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        qty = utils.size_to_qty(self.capital * 0.1, self.price, fee_rate=self.fee_rate)

        self.buy = qty, self.price
        self.take_profit = qty, self.price + (self.price * 0.15)
        self.stop_loss = qty, self.price - (self.price * 0.05)

    def go_short(self):
        qty = utils.size_to_qty(self.capital * 0.1, self.price, fee_rate=self.fee_rate)

        self.sell = qty, self.price
        self.take_profit = qty, self.price - (self.price * 0.15)
        self.stop_loss = qty, self.price + (self.price * 0.05)

    def update_position(self):
        if self.is_long:
            if self.close > self.average_entry_price + (
                self.average_entry_price * 0.02
            ):
                self.stop_loss = self.position.qty, self.average_entry_price + (
                    self.average_entry_price * 0.02
                )
        if self.is_short:
            if self.close < self.average_entry_price - (
                self.average_entry_price * 0.02
            ):
                self.stop_loss = self.position.qty, self.average_entry_price - (
                    self.average_entry_price * 0.02
                )

    @property
    def bullish(self):
        return self.close > self.open

    @property
    def bearish(self):
        return self.close < self.open

    @property
    def bb(self):
        return ta.bollinger_bands(self.candles)

    def hyperparameters(self):
        return [
            {
                "name": "take_profit_value",
                "type": int,
                "min": 1,
                "max": 100,
                "default": 10,
            },
            {
                "name": "stop_loss_value",
                "type": int,
                "min": 1,
                "max": 100,
                "default": 10,
            },
        ]
