"""
单只股票的基础结构
"""
from dataclasses import field, dataclass
from typing import List
from modules.tick import Tick
from modules.trigger import BuyTrigger, SellTrigger
from modules.position import Position

from utils import time_utils
from utils.log_utils import v_round
import config
from datetime import datetime


@dataclass
class Stock:
    stock_code: str = field(default="000001")
    stock_code_ts: str = field(default="000001.SZ")
    stock_name: str = field(default="")
    market: str = field(default="")
    ipo_date_str: str = field(default="")
    basic_info: dict = field(default=dict)

    # 实盘数据及指标数据
    tick: Tick = field(default_factory=Tick)

    # 持仓信息
    position: Position = field(default_factory=Position)

    # 当天是否触发过买入提醒
    buy_trigger: BuyTrigger = field(default_factory=BuyTrigger)
    sell_trigger: SellTrigger = field(default_factory=SellTrigger)

    @property
    def log_name(self):
        return "|" + self.stock_code + "." + self.stock_name + " " + self.market + "|"

    @property
    def log_tick(self):
        return self.log_name + "<br>\n" + self.tick.log

    @property
    def log_position(self):
        return f"- [已持有股票：{self.log_name}]<br> \n" \
               f"-- 可用/买入份额: {self.position.can_use_size} / {self.position.buy_size}, {'当日已售出' if self.position.today_sell else ''} <br> \n" \
               f"-- 买入价: {v_round(self.position.buy_price)}元" \
               f"买入总价格：{self.position.buy_value}元, 【建仓日期: {self.position.position_date}】, " \
               f"历史最高价：{self.position.max_price_during_position} ({v_round(self.position.max_increase_ratio_during_position * 100)}%), " \
               f"历史最低价：{self.position.min_price_during_position} ({v_round(self.position.min_decline_ratio_during_position * 100)}%)<br>\n" \
               f"-- 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" \
               f"-- 当前价格: {self.tick.price}元, 现股票价值: {self.position.now_value}元, " \
               f"{'盈利' if self.position.now_price >= self.position.buy_price else '亏损'} {abs(self.position.now_benefit)}元 " \
               f"({v_round(self.position.now_benefit_rate * 100)}%); | " \
               f"当前MA20: {v_round(self.tick.ma_20)}, 持仓区间:{v_round(self.position.static_SL_price)} ~ {v_round(self.position.static_TP_price)}元<br>\n" \
               f"-- 历史最高价: {v_round(self.position.max_price_during_position)}元, 【动态止盈价格: {v_round(self.position.dynamic_TP_price)}元】, " \
               f"【静态止盈价: {v_round(self.position.static_TP_price)}元】, 对应止盈率 {round(config.STATIC_TP_RATIO * 100, 1)}%,  " \
               f"【静态止跌价: {v_round(self.position.static_SL_price)}元】, 对应止损率 {round(config.STATIC_SL_RATIO * 100, 1)}% "

    @property
    def log_buy_strategy(self):
        return f"- [触发买入条件股票：{self.log_name}]\n" \
               f"-- 今日触发【{self.buy_trigger.trigger_times}】次, 预期买入价: {self.buy_trigger.expect_price}元，买入类型为[{self.buy_trigger.price_info}], " \
               f"({self.buy_trigger.expect_min_price} ~ {self.buy_trigger.expect_max_price})元, 预期买入份额: 【{self.buy_trigger.expect_buy_size}】"

    @property
    def log_sell_strategy(self):
        return f"- [触发卖出条件股票：{self.log_name}]\n" \
               f"-- 今日触发【{self.sell_trigger.trigger_times}】次, 【{'止盈' if self.sell_trigger.is_TP else '止跌'}】, 以{self.sell_trigger.price_info}类型卖出" \
               f"当前股价: {v_round(self.tick.price)}, 当前MA20: {v_round(self.tick.ma_20)}, 持仓区间:{v_round(self.position.static_SL_price)} ~ {v_round(self.position.static_TP_price)}元 <br>\n" \
               f"-- 预期卖出价: {self.sell_trigger.expect_price}元 ({self.sell_trigger.expect_min_price} ~ {self.sell_trigger.expect_max_price})元, 卖出类型为[{self.sell_trigger.price_info}], " \
               f"预期卖出份额: 【{self.position.can_use_size}】\n" \
               f"-- 参考信息: 当前动态止盈价{v_round(self.position.dynamic_TP_price)}元, 静态止损价{v_round(self.position.static_SL_price)}元"

    def init_max_and_min_price(self, no_price_data: bool = False):
        """
        计算从该股减仓以来，最高股价及最低股价
        """
        # df = time_utils.tushare_api().daily(ts_code=self.stock_code_ts, start_date=self.position.position_date,
        #                                     end_date=time_utils.today())
        #
        # # 提取最高价和最低价的最大值和最小值
        # max_price = df['high'].max()
        # min_price = df['low'].min()

        self.position.renew_max_price(float(self.basic_info["最高价"] if self.basic_info["最高价"] != '-' else 0))
        self.position.renew_min_price(float(self.basic_info["最低价"] if self.basic_info["最高价"] != '-' else 0))

        # if no_price_data:
        #     price = df['close'].iloc[-1]
        #     self.tick.price = price
        # else:
        #     self.tick.price = self.position.now_price
