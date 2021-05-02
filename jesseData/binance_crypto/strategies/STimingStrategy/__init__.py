import jesse.indicators as ta
from jesse import utils
from jesse.strategies import Strategy, cached

STOP_LOSS_PERCENT = 0.05
CAPITAL_PERCENT = 0.1
PIKE_PERCENT = 5


def calculate_percent(value: float, reference: float) -> float:
    return (abs(value - reference) / reference) * 100


class STimingStrategy(Strategy):
    def __init__(self):
        super().__init__()

        self.current_pyramiding_levels = 0

    def should_short(self) -> bool:
        # Detect small pike
        return calculate_percent(self.close, self.long_ema) > PIKE_PERCENT

    def should_cancel(self) -> bool:
        return True

    def go_short(self):
        qty = utils.size_to_qty(
            self.capital * CAPITAL_PERCENT, self.price, fee_rate=self.fee_rate
        )
        self.take_profit = qty, self.long_ema

        self.sell = qty, self.price
        self.stop_loss = qty, self.price + (self.price * STOP_LOSS_PERCENT)
        self.current_pyramiding_levels = self.price

    def go_long(self):
        pass

    def update_position(self):
        if self.is_short:
            # Follow the price if the price raised.
            if self.close < self.current_pyramiding_levels * 1.02:
                self.current_pyramiding_levels = self.current_pyramiding_levels - (
                    self.current_pyramiding_levels * 0.01
                )
                self.stop_loss = self.position.qty, self.current_pyramiding_levels

    @property
    def long_ema(self):
        return ta.ema(self.candles, 60)
