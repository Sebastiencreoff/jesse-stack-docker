import jesse.indicators as ta
from jesse import utils
from jesse.strategies import Strategy, cached


class TestStrat(Strategy):
    def should_long(self) -> bool:
        return True

    def should_short(self) -> bool:
        return False

    def should_cancel(self) -> bool:
        # Useless for live trading.
        return False

    def go_long(self):
        breakpoint()
        qty = utils.size_to_qty(self.capital * 0.1, self.price, fee_rate=self.fee_rate)
        self.take_profit = qty, 200000

        self.buy = qty, self.price
        self.stop_loss = qty, 10
        self.current_pyramiding_levels = self.price

        print(f"LONG buy: qty: {qty}, price:{self.price}")
        print(f"LONG take_profit: qty: {qty}, price:200000")
        print(f"LONG stop_loss: qty: {qty}, price:10")
        breakpoint()

    def go_short(self):
        pass

    def update_position(self):
        pass
