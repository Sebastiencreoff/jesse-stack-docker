import jesse.indicators as ta
from jesse import utils
from jesse.strategies import Strategy, cached

from .indicators import kdj

TAKE_PROFIT_PERCENT = 0.05
STOP_LOSS_PERCENT = 0.05
UPDATE_PERCENT = 0.02
CAPITAL_PERCENT = 0.1


def calculate_percent(value: float, reference: float) -> float:
    return (abs(value - reference) / reference) * 100


class LSGridStrategy(Strategy):
    def should_long(self) -> bool:
        if self.bullish:
            # If close is lower than 10% of the lowerband
            if (
                calculate_percent(self.bb.lowerband, self.bb.upperband) > 5
                and calculate_percent(self.close, self.bb.lowerband) < 2
            ):
                return True

        return False

    def should_short(self) -> bool:
        if self.bearish:
            # If close is lower than 10% of the lowerband
            if (
                calculate_percent(self.bb.lowerband, self.bb.upperband) > 5
                and calculate_percent(self.bb.upperband, self.close) < 2
            ):
                return True

        return False

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        qty = utils.size_to_qty(
            self.capital * CAPITAL_PERCENT, self.price, fee_rate=self.fee_rate
        )

        if self.price >= self.bb.middleband:
            self.take_profit = qty, self.bb.upperband
        else:
            self.take_profit = [
                (qty / 2, self.bb.middleband),
                (qty / 2, self.bb.upperband),
            ]

        self.buy = qty, self.price
        self.stop_loss = qty, self.price - (self.price * STOP_LOSS_PERCENT)

    def go_short(self):
        qty = utils.size_to_qty(self.capital * 0.1, self.price, fee_rate=self.fee_rate)

        self.sell = qty, self.price

        if self.price > self.bb.middleband:
            self.take_profit = [
                (qty / 2, self.bb.middleband),
                (qty / 2, self.bb.lowerband),
            ]

        else:
            self.take_profit = qty, self.bb.lowerband

        self.stop_loss = qty, self.price + (self.price * STOP_LOSS_PERCENT)

    def update_position(self):
        if self.is_long:
            if self.close > self.bb.middleband:
                self.stop_loss = self.position.qty, self.bb.middleband

        if self.is_short:
            if self.close < self.bb.middleband:
                self.stop_loss = self.position.qty, self.bb.middleband

    @property
    def bullish(self):
        return self.close > self.open

    @property
    def bearish(self):
        return self.close < self.open

    @property
    def bb(self):
        return ta.bollinger_bands(self.candles)

    @property
    def kdj(self):
        return kdj(self.candles)

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
