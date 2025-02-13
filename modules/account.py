"""
账户系统，管理现金、价值、持仓股
"""
from dataclasses import field, dataclass
from typing import List
import os
import pandas as pd
import openpyxl
from utils import time_utils
import requests
import config
import json
from modules.stock import Stock
from modules.stock_pool import StockPool
from datetime import datetime


@dataclass
class Account:
    original_cash: float = field(default=0)

    cash: float = field(default=0)
    stock_value: float = field(default=0)

    position_stocks: List[Stock] = field(default_factory=list)
    customized_position_info: dict = field(default=dict)  # 自定义持仓信息

    @property
    def cannot_use_cash(self):
        # """
        # 预留金额，避免满仓: 可以按原现金和现有现金的10%来算
        # """:
        # return 0
        if self.cash <= self.original_cash:
            return self.original_cash * config.CANNOT_USE_CASH_RATE
        else:
            return self.cash * config.CANNOT_USE_CASH_RATE

    @property
    def can_use_cash(self):
        can_use_cash = self.cash - self.cannot_use_cash
        if can_use_cash <= 0:
            return 0
        else:
            return can_use_cash

    @property
    def single_stock_max_buy_value(self):
        """
        单股最大买入量: 可以按原现金和现有现金的50%来算
        """
        # if self.cash <= self.original_cash:
        #     return self.original_cash * config.MAX_POSITION_RATE
        # else:
        #     return self.cash * config.MAX_POSITION_RATE
        return config.MAX_VALUE

    def init_original_info(self, original_cash: float):
        self.original_cash = original_cash

    @property
    def total_value(self): return self.cash + self.stock_value

    def add_customized_strategy(self, customized_strategy: dict, stock_pool: StockPool, log):
        """
        定制的个股止盈、止损设置
        """
        for stock_code in customized_strategy.keys():
            for stock in stock_pool.all_stock:
                if stock.stock_code == stock_code:
                    # 如果有价格优先用价格
                    if customized_strategy[stock_code][2] != 0:
                        stock.position.static_tp_ratio = customized_strategy[stock_code][2] / max(stock.position.buy_price, 1) - 1
                    else:
                        stock.position.static_tp_ratio = customized_strategy[stock_code][0]

                    if customized_strategy[stock_code][3] != 0:
                        stock.position.static_sl_ratio = customized_strategy[stock_code][3] / max(stock.position.buy_price, 1) - 1
                    else:
                        stock.position.static_sl_ratio = customized_strategy[stock_code][1]

                    log.log(f"【已将 {stock.log_name} 设置为 "
                            f"止盈率 {round(stock.position.static_tp_ratio * 100, 1)}% "
                            f"止损率 {round(stock.position.static_sl_ratio * 100, 1)}% 】")
                    break

    def auto_init_account(self, stock_pool: StockPool):
        response = requests.get(f"{config.ACCOUNT_BASE_URL}/balance")
        data = response.json()
        print("同花顺账户信息:", data)
        self.cash = data["可用金额"]
        self.stock_value = data["股票市值"]
        self.original_cash = config.ORIGINAL_CASH

        response = requests.get(f"{config.ACCOUNT_BASE_URL}/position")
        data = response.json()
        print("同花顺持仓信息:", data)

        for each_data in data:
            stock_code = each_data["证券代码"]
            buy_price = each_data["成本价"]
            buy_size = each_data["股票余额"]
            can_use_size = each_data["可用余额"]
            now_price = each_data["市价"]

            if stock_code == "400207":
                continue

            if "持股天数" in each_data.keys():
                position_date = each_data["持股天数"]
            else:
                position_date = 2

            if buy_price <= 0.1:
                continue

            # now_value = each_data["市值"]
            # now_benefit = each_data["盈亏"]
            # now_benefit_rate = each_data["盈亏比例(%)"]

            if stock_code in self.customized_position_info.keys():
                # 已手动录入持仓信息
                buy_date = self.customized_position_info[stock_code]
            elif can_use_size == 0:
                buy_date = time_utils.today()
            else:
                if position_date >= 1:
                    # buy_date = time_utils.last_trade_day(-position_date)

                    from modules.downloader import crawler
                    trade_day_list = crawler.get_current_trade_day()
                    buy_date, __ = trade_day_list[-2:]

                else:
                    # 先默认上一个交易日last_trade_day
                    # buy_date = time_utils.last_trade_day(-2)
                    buy_date = time_utils.today()

            find_stock = False
            for stock in stock_pool.all_stock:
                if stock.stock_code == stock_code:
                    stock.position.init_holding(buy_price, buy_size, can_use_size, now_price, buy_date)
                    self.position_stocks.append(stock)
                    find_stock = True

            # 不在股票池种需要添加
            if not find_stock:
                temp_stock = stock_pool.add_stock_by_code(stock_code)
                print(f"已添加一只不在股票池中的持仓股: {temp_stock.log_name}, 持仓日期: {buy_date}")

        self.init_position(no_price_data=False)

    def manual_init_account(self, stock_pool: StockPool, cash):
        self.cash = cash

        for stock in stock_pool.all_stock:
            if stock.position.has_position:
                self.position_stocks.append(stock)

        self.init_position(no_price_data=True)

        # 更新已有股票价值
        self.stock_value = 0
        for stock in self.position_stocks:
            self.stock_value += stock.position.buy_value

    def add_stock_in_position(self, stock: Stock):
        self.position_stocks.append(stock)

    def init_position(self, no_price_data: bool = False):
        # 需要更新持仓后的股票最大值及最小值
        for stock in self.position_stocks:
            stock.init_max_and_min_price(no_price_data=no_price_data)
            # print(stock)

    def renew_position_by_tick(self):
        """
        根据每次的Tick数据，更新持仓信息
        """
        self.stock_value = 0
        for stock in self.position_stocks:
            stock.position.now_price = stock.tick.price
            stock.position.renew_max_price(stock.tick.high)
            stock.position.renew_min_price(stock.tick.low)
            self.stock_value += stock.position.buy_size * stock.tick.price

    @property
    def log(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = f"<br>\n" \
                 f"{current_time}【当前账户总资产{self.total_value}元，现金：{self.cash}元，" \
                f"股票价值：{self.stock_value}元，持仓股票数：{len(self.position_stocks)}】<br>\n" \
                 f"【单股最大买入量: {round(self.single_stock_max_buy_value, 2)}元, 不可交易的现金设置为: {round(self.cannot_use_cash, 2)}元, 可用交易的现金剩余: {round(self.can_use_cash, 2)}元】<br>\n" \
                 f"<br>\n"
        for stock in self.position_stocks:
            output += stock.log_position + "<br>\n"
        return output

    @staticmethod
    def send_order(stock_code: str, price: float, amount: int, singal: str, stock_name: str, head: str, info: str):
        data = {
            "action": singal,
            "code": stock_code,
            "price": round(price, 2),
            "amount": amount,
            "stock_name": stock_name,
            "head": head,
            "info": info
        }

        print("data: ", data)
        response = requests.post(f"{config.ACCOUNT_BASE_URL}/order", json=data)

        if response.status_code == 200:
            # 读取委托合同编号
            data = response.json()
            # entrust_number = data["entrust_no"]
            return True
        else:
            return False

    def have_sell_stock(self, stock_pool: StockPool, is_manual: bool = False):
        if is_manual:
            pass
        else:
            self.auto_init_account(stock_pool)

