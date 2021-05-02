import jesse.indicators as ta
from jesse import utils
from jesse.strategies import Strategy, cached

TAKE_PROFIT_PERCENT = 1.05
STOP_LOSS_PERCENT = 0.015
CAPITAL_PERCENT = 0.2
PIKE_PERCENT = 6
UPDATE_PERCENT = 0.013
NB_CONSEQ = 2


def calculate_percent(value: float, reference: float) -> float:
    return ((value - reference) / reference) * 100


class LSTimingStrategy(Strategy):
    def __init__(self):
        super().__init__()

        self.current_pyramiding_levels = 0
        self.max_drop = 0
        self.max_peak = 0

    def should_long(self) -> bool:
        # Detect small drop
        # previous = self.max_drop
        self.max_drop = min(self.max_drop, calculate_percent(self.close, self.long_ema))
        # if previous != self.max_drop:
        #     print(f" MAX DROP: {self.max_drop}")
        return calculate_percent(
            self.close, self.long_ema
        ) < -PIKE_PERCENT and utils.strictly_increasing(self.candles[1], NB_CONSEQ)

    def should_short(self) -> bool:
        # Detect small pike
        # previous = self.max_peak
        self.max_peak = max(self.max_peak, calculate_percent(self.close, self.long_ema))
        # if previous != self.max_peak:
        #     print(f" MAX PIKE: {self.max_peak}")
        return calculate_percent(
            self.close, self.long_ema
        ) > PIKE_PERCENT and utils.strictly_decreasing(self.candles[1], NB_CONSEQ)

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        qty = utils.size_to_qty(
            self.capital * CAPITAL_PERCENT, self.price, fee_rate=self.fee_rate
        )
        self.take_profit = qty, self.long_ema * TAKE_PROFIT_PERCENT

        self.buy = qty, self.price
        self.stop_loss = qty, self.price - (self.price * STOP_LOSS_PERCENT)
        self.current_pyramiding_levels = self.price

    def go_short(self):
        qty = utils.size_to_qty(
            self.capital * CAPITAL_PERCENT, self.price, fee_rate=self.fee_rate
        )
        self.take_profit = qty, self.long_ema / TAKE_PROFIT_PERCENT

        self.sell = qty, self.price
        self.stop_loss = qty, self.price + (self.price * STOP_LOSS_PERCENT)
        self.current_pyramiding_levels = self.price

    def update_position(self):
        if self.is_long:
            # Follow the price if the price raised.
            if self.close > self.current_pyramiding_levels * (1 + 3 * UPDATE_PERCENT):
                self.current_pyramiding_levels = self.current_pyramiding_levels + (
                    self.current_pyramiding_levels * UPDATE_PERCENT
                )
                self.stop_loss = self.position.qty, self.current_pyramiding_levels
        if self.is_short:
            # Follow the price if the price dropped.
            if self.close < self.current_pyramiding_levels * (1 - 3 * UPDATE_PERCENT):
                self.current_pyramiding_levels = self.current_pyramiding_levels - (
                    self.current_pyramiding_levels * UPDATE_PERCENT
                )
                self.stop_loss = self.position.qty, self.current_pyramiding_levels

    @property
    def bullish(self):
        return self.close > self.open

    @property
    def bearish(self):
        return self.close < self.open

    @property
    def long_ema(self):
        return ta.ema(self.candles, 60)
