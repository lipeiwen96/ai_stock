from dataclasses import field, dataclass
from typing import List
from utils.log_utils import v_round
from utils.math_utils import robust_divide
import config


@dataclass
class Position:
    has_position: bool = field(default=False)
    today_sell: bool = field(default=False)
    today_buy: bool = field(default=False)

    position_date: str = field(default=str)  # 持仓的日期

    position_day_num: int = field(default=0)
    buy_price: float = field(default=0)
    buy_size: int = field(default=0)
    can_use_size: int = field(default=0)  # 可用余额

    now_price: float = field(default=0)  # 动态刷新价格的关键

    max_price_during_position: float = field(default=0)  # 持仓期间最高股价
    max_increase_ratio_during_position: float = field(default=0)  # 持仓期间最大涨幅
    min_price_during_position: float = field(default=0)
    min_decline_ratio_during_position: float = field(default=0)

    # static_sl_ratio: float = field(default=0)  # 止损率
    # static_tp_ratio: float = field(default=0)  # 止盈率

    @property
    def buy_value(self):
        return v_round(self.buy_price * self.buy_size)

    @property
    def now_value(self):
        return v_round(self.now_price * self.buy_size)

    @property
    def now_benefit(self):
        return v_round(self.now_value - self.buy_value)

    @property
    def now_benefit_rate(self):
        return round(robust_divide(self.now_benefit, self.buy_value), 4)

    @property
    def static_TP_price(self):
        """
        静态止盈价格
        """
        return self.buy_price * (1 + config.STATIC_TP_RATIO)

    @property
    def static_SL_price(self):
        """
        静态止跌价格
        """
        return self.buy_price * (1 - config.STATIC_SL_RATIO)

    @property
    def dynamic_TP_price(self):
        """
        动态止盈价格
        """
        return self.buy_price + (self.max_price_during_position - self.buy_price) * config.DYNAMIC_TP_RATIO

    def close_out(self):
        """
        清仓操作
        """
        self.has_position = True  # 仍然在持仓库里
        self.today_sell = True
        self.position_date = ""
        self.buy_price = self.now_price = 0
        self.buy_size = self.can_use_size = 0
        self.max_price_during_position = self.max_increase_ratio_during_position = self.min_price_during_position = self.min_decline_ratio_during_position = 0

    def init_holding(self, buy_price, buy_size, can_use_size, now_price, buy_date: str):
        """
        初始化已有持仓
        """
        self.has_position = True
        self.position_date = buy_date

        if buy_size == 0:
            self.today_sell = True

        self.buy_price = buy_price
        self.buy_size = buy_size
        self.can_use_size = can_use_size
        self.now_price = now_price

        self.max_price_during_position = self.min_price_during_position = buy_price  # 这个价格需要重新设定
        self.max_increase_ratio_during_position = self.min_decline_ratio_during_position = 0  # 这个涨跌幅需要重新设定

    def buy_action(self, buy_price, buy_size, position_date: str, is_today: bool = False):
        """
        今日内买入，不可卖出
        """
        self.has_position = True
        self.position_date = position_date

        self.buy_price = buy_price
        self.buy_size = buy_size

        if is_today:
            self.can_use_size = 0
        else:
            self.can_use_size = buy_size

        self.now_price = buy_price
        self.max_price_during_position = self.min_price_during_position = buy_price  # 这个价格需要重新设定
        self.max_increase_ratio_during_position = self.min_decline_ratio_during_position = 0  # 这个涨跌幅需要重新设定

    def renew_max_price(self, max_price):
        if max_price > self.max_price_during_position:
            self.max_price_during_position = max_price
            self.compute_max_increase_ratio_during_position(price=max_price)

    def renew_min_price(self, min_price):
        if min_price < self.min_price_during_position:
            self.min_price_during_position = min_price
            self.compute_min_decline_ratio_during_position(price=min_price)

    def compute_max_increase_ratio_during_position(self, price):
        self.max_increase_ratio_during_position = round(robust_divide((price - self.buy_price), self.buy_price), 4)

    def compute_min_decline_ratio_during_position(self, price):
        self.min_decline_ratio_during_position = round(robust_divide((price - self.buy_price), self.buy_price), 4)
