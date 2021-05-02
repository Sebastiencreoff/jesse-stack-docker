import jesse.indicators as ta
from jesse import utils
from jesse.strategies import Strategy, cached


def calculate_percent(value: float, reference: float) -> float:
    return (abs(value - reference) / reference) * 100


class SampleTrendFollowing(Strategy):
    def should_long(self) -> bool:
        return self.short_ema > self.long_ema

    def should_short(self) -> bool:
        return self.short_ema < self.long_ema

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        entry = self.price
        stop = entry - 3 * self.atr
        qty = utils.risk_to_qty(self.capital, 3, entry, stop, self.fee_rate)
        profit_target = entry + 5 * self.atr

        self.buy = qty, entry
        self.stop_loss = qty, stop
        self.take_profit = qty, profit_target

    def go_short(self):
        entry = self.price
        stop = entry + 3 * self.atr
        qty = utils.risk_to_qty(self.capital, 3, entry, stop, self.fee_rate)
        profit_target = entry - 5 * self.atr

        self.sell = qty, entry
        self.stop_loss = qty, stop
        self.take_profit = qty, profit_target

    @property
    def long_ema(self):
        return ta.ema(self.candles, 50)

    @property
    def short_ema(self):
        return ta.ema(self.candles, 21)

    @property
    def atr(self):
        return ta.atr(self.candles)
