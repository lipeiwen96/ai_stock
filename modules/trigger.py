"""
单只股票的买卖提醒
"""
from dataclasses import field, dataclass
from typing import List


@dataclass
class Trigger:
    today_meet: bool = field(default=False)  # 当日是否触发
    already_execute: bool = field(default=False)  # 是否以及按照触发来买入

    expect_price: float = field(default=0)
    price_info: str = field(default="")  # 买入价信息

    all_expect_price_list: List[float] = field(default_factory=list)
    expect_min_price: float = field(default=0)  # 动态最低价格
    expect_max_price: float = field(default=0)  # 动态最高价格

    trigger_times: int = field(default=0)  # 触发次数
    notification_times: int = field(default=0)  # E-mail通知次数

    def add_expect_price(self, price: float):
        self.all_expect_price_list.append(price)
        self.expect_price = price
        self.expect_min_price = min(self.expect_min_price, price)
        self.expect_max_price = max(self.expect_max_price, price)

    def add_trigger(self, price, price_info: str = ""):
        if not self.today_meet:
            self.today_meet = True
            self.expect_max_price = self.expect_min_price = self.expect_price = price
            self.price_info = price_info

        if self.already_execute:
            self.trigger_times += 1
        else:
            self.add_expect_price(price)
            self.trigger_times += 1

    @property
    def can_notification(self):
        if self.notification_times > 3:
            return False
        if self.trigger_times == 1:
            return True
        elif self.trigger_times % 10 == 0:
            return True
        else:
            return False


@dataclass
class BuyTrigger(Trigger):
    expect_buy_size: int = field(default=0)

    def todo(self):
        pass


@dataclass
class SellTrigger(Trigger):
    # 止盈：Take Profit (TP) | 止跌：Stop Loss (SL)
    is_TP: bool = field(default=False)

    def todo(self):
        pass

