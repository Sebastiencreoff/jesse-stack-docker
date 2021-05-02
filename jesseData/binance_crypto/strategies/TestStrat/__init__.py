import jesse.indicators as ta
from jesse import utils
from jesse.strategies import Strategy, cached


class TestStrat(Strategy):
    def should_long(self) -> bool:
        return True

    def should_short(self) -> bool:
        return False

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        qty = utils.size_to_qty(self.capital * 0.1, self.price, fee_rate=self.fee_rate)
        self.take_profit = qty, 200000

        self.buy = qty, self.price
        self.stop_loss = qty, 10
        self.current_pyramiding_levels = self.price

    def go_short(self):
        pass

    def update_position(self):
        pass
