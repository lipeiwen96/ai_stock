"""
核心程序
"""
from dataclasses import field, dataclass
from typing import List
import os
import time

import hashlib
from pathlib import Path

import config
from utils import email_sender, time_utils

from modules.downloader import crawler
from utils.path_utils import PathUtils
from modules.stock_pool import StockPool
from modules.account import Account
from modules.strategy import Strategy
from logger import Logger


@dataclass
class HeartBeat:
    monitoring_beat: int = field(default=0)
    trading_beat: int = field(default=0)

    @property
    def total_beat(self): return self.trading_beat + self.monitoring_beat

    @property
    def log(self):
        return f"监听期刷新数-{self.monitoring_beat}, 交易期刷新数-{self.trading_beat}, 总刷新数-{self.total_beat}"


@dataclass
class CoreBrain:
    stock_pool: StockPool = field(default_factory=StockPool)
    account: Account = field(default_factory=Account)

    scode_list: List[str] = field(default_factory=list)
    last_dict: dict = field(default=dict)  # 历史数据

    now: str = field(default=str)
    # 心跳记录
    heart_beat: HeartBeat = field(default_factory=HeartBeat)

    send_email_status: bool = field(default=False)

    log: Logger = field(default_factory=Logger)

    def init(self, stock_pool: StockPool, account: Account, send_email_status):
        self.stock_pool = stock_pool
        self.account = account
        self.send_email_status = send_email_status
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        self.scode_list = [stock.stock_code for stock in self.stock_pool.all_stock]
        self.scode_list.insert(0, "1.000001")
        # print(self.scode_list)

        self.stock_pool.szzz.stock_code = "1.000001"
        self.stock_pool.szzz.stock_name = "上证综指"

    def add_cache(self, from_date):
        """
        缓存历史日线数据，淘宝写的，用这个来计算历史的数据，存至data/文件夹
        """
        trade_day_list = crawler.get_current_trade_day()
        yesterday, today = trade_day_list[-2:]
        self.log.log(f"- 时间校验，昨天日期为: {yesterday}, 今天日期为: {today}；当前时刻: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")

        if not os.path.exists("data"):
            os.mkdir("data")

        # 缓存机制
        kline_file = Path(f"data/{today}.pkl")

        # 检查是否存在今日的缓存文件
        if kline_file.exists():
            self.last_dict = crawler.load_cached_data(kline_file)
            self.log.log("历史数据已从今日缓存中加载。")
        else:
            # 删除旧的缓存文件
            for file in Path("data").glob("*.pkl"):
                file.unlink()

            # 重新计算并缓存
            self.last_dict = crawler.get_last_data(self.scode_list, kline_file, from_date.strftime('%Y-%m-%d'))
            self.log.log("历史数据重新计算并缓存。")

    def renew_tick(self):
        """
        通用Tick数据刷新接口
        """
        # 更新时刻
        start_time = time.time()
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 更新最新Tick数据
        data_list = []
        data_list = crawler.get_hs_data(self.last_dict, self.scode_list)
        if len(data_list) != 0:
            for item in data_list:
                if item["股票代码"] == "1.000001":
                    # print(item)
                    self.stock_pool.szzz.tick.renew(item=item, total_beat_id=self.heart_beat.total_beat)
                else:
                    index = self.scode_list.index(item["股票代码"]) - 1
                    if item["最新价"] == "-":
                        print(f"--- {self.stock_pool.all_stock[index].log_name} 当前停盘，无法获取数据")
                        continue
                    stock = self.stock_pool.all_stock[index]
                    # print(item)
                    stock.tick.renew(item=item, total_beat_id=self.heart_beat.total_beat)

        end_time = time.time()
        self.log.log(f"【纯数据爬取】第{self.heart_beat.total_beat}次调用完成，用时 {round(end_time-start_time, 2)}秒 \n")

        for stock in self.stock_pool.all_stock:
            print(stock.log_tick)
        print(self.stock_pool.szzz.log_tick)

        # 更新持仓股数据及当前资金
        self.account.renew_position_by_tick()
        self.log.log(self.account.log)

        end_time = time.time()
        self.log.log(f"【数据刷新接口】第{self.heart_beat.total_beat}次调用完成，用时 {round(end_time-start_time, 2)}秒 \n")

    def execute_strategy(self):
        """
        执行判断策略
        """
        start_time = time.time()

        Strategy.execute_strategy(now=self.now, stock_pool=self.stock_pool, account=self.account, log=self.log)
        self.stock_pool.strategy_log(self.log)

        end_time = time.time()
        self.log.log(f"【策略判定接口】第{self.heart_beat.total_beat}次调用完成，用时 {round(end_time - start_time, 2)}秒 \n")

    def execute_order(self):
        """
        执行订单
        """
        start_time = time.time()

        # 单次订单执行总数
        order_id = 0
        NUM_LIMIT = 1

        # 先卖
        for stock in self.stock_pool.all_stock:
            if stock.sell_trigger.today_meet:
                if not stock.sell_trigger.already_execute and order_id <= NUM_LIMIT:
                    stock_name = stock.log_name
                    head = f"{stock.sell_trigger.price_info}类型，卖出于{round(stock.tick.price, 2)}元"
                    info = f"""【持仓信息】{stock.log_position} 【当前股票信息】{stock.tick.log} 【触发原因】{stock.log_sell_strategy}"""

                    self.log.log(f"【交易明细】当前时间{self.now}，交易行为：{head}\n")
                    self.log.log(f"{info}\n")

                    # 执行挂单操作
                    status = Account.send_order(stock_code=stock.stock_code,
                                                price=round(stock.tick.price, 2),  # 现价卖
                                                amount=stock.position.can_use_size, singal="sell",
                                                stock_name=stock_name, head=head,
                                                info=info)

                    # TODO: 挂单查询及状态更新
                    if status:
                        stock.sell_trigger.already_execute = True

                        # # 更新账号余额及价值
                        self.account.cash += stock.position.can_use_size * stock.sell_trigger.expect_price
                        # self.account.manual_init_account(cash=self.account.cash, stock_pool=self.stock_pool)

                        order_id += 1

                        # 邮箱通知
                        email_sender.sell_message_sender(stock=stock, now=self.now, start=self.send_email_status)
                        stock.sell_trigger.notification_times += 1

                        # 清空持仓信息
                        # 当日卖出的股仍显示在账号中，不进行删除
                        stock.position.close_out()

                    else:
                        pass

        # 后买
        for stock in self.stock_pool.all_stock:
            if stock.buy_trigger.today_meet:
                stock_name = stock.log_name
                head = f"{stock.buy_trigger.price_info}类型，买入于{round(stock.tick.price, 2)}元"
                info = f"""{stock.log_name} 触发买入交易条件: 【当前股票信息】{stock.tick.log} 【触发原因】{stock.log_buy_strategy}"""
                if stock.buy_trigger.expect_buy_size == 0:
                    continue

                if not stock.buy_trigger.already_execute and order_id <= NUM_LIMIT:
                    # 执行挂单操作
                    # 当前价格远高于买入价
                    if stock.tick.price > stock.buy_trigger.expect_price * (1 + 0.02):
                        price = stock.tick.price
                        status = Account.send_order(stock_code=stock.stock_code,
                                                    price=round(stock.tick.price, 2),  # 现价卖
                                                    amount=stock.buy_trigger.expect_buy_size, singal="buy",
                                                    stock_name=stock_name, head=head,
                                                    info=info)

                    else:
                        price = stock.buy_trigger.expect_price
                        status = Account.send_order(stock_code=stock.stock_code,
                                                    price=stock.buy_trigger.expect_price,
                                                    amount=stock.buy_trigger.expect_buy_size, singal="buy",
                                                    stock_name=stock_name, head=head,
                                                    info=info)

                    # TODO: 挂单查询及状态更新
                    if status:
                        stock.buy_trigger.already_execute = True
                        stock.position.buy_action(price, stock.buy_trigger.expect_buy_size, time_utils.today(), True)

                        # # 更新账号余额及价值
                        self.account.cash -= stock.buy_trigger.expect_buy_size * stock.buy_trigger.expect_price * (1 + config.COMMISSION_RATE)
                        self.account.add_stock_in_position(stock)  # 增加持仓
                        order_id += 1

                        # 邮箱通知
                        # if stock.buy_trigger.can_notification and order_id <= NUM_LIMIT:
                        email_sender.buy_message_sender(stock=stock, now=self.now, start=self.send_email_status)
                        stock.buy_trigger.notification_times += 1
                    else:
                        pass

        end_time = time.time()
        self.log.log(self.account.log)
        self.log.log(f"【下单接口】第{self.heart_beat.total_beat}次调用完成，用时 {round(end_time - start_time, 2)}秒 \n")

    def in_monitoring_renew(self):
        """
        监听状态刷新
        """
        self.log.log(f"\n-- 当前时间 {self.now} 处于【监听期间】 | 开始更新 【HEART ID: {self.heart_beat.log}】")
        self.renew_tick()

        self.heart_beat.monitoring_beat += 1

    def in_trade_renew(self):
        """
        实盘状态刷新
        """
        self.log.log(f"\n-- 当前时间 {self.now} 处于【实盘期间】 | 开始更新 【HEART ID: {self.heart_beat.log}】")
        self.renew_tick()
        self.execute_strategy()
        self.execute_order()

        self.heart_beat.trading_beat += 1
