"""
股票池
"""
import tushare as ts
from dataclasses import field, dataclass
from typing import List
import os
import pandas as pd
import openpyxl

import config
from utils import time_utils

from modules.stock import Stock
from modules.downloader.get_stock_info import get_random_stock_code_and_name_list, get_total_stock_code
from modules.downloader.crawler import get_basic_data_info


@dataclass
class StockPool:
    # 大盘
    szzz: Stock = field(default_factory=Stock)
    all_stock: List[Stock] = field(default_factory=list)
    start_date: str = field(default=str)
    now_date: str = field(default=str)

    @property
    def my_stock_num(self):
        return len(self.all_stock)

    @property
    def all_stock_info(self):
        output = ""
        i = 0
        for stock in self.all_stock:
            output += f"ID{i}. {stock.stock_code}: {stock.stock_name} | "
        return output

    def init_time(self, start_date: str = "2022-10-22"):
        now_date = time_utils.now()
        self.start_date = start_date
        self.now_date = f"{now_date[:4]}-{now_date[4:6]}-{now_date[6:8]}"

    def create_random_pool(self, stock_num: int = 10, max_plot_num: int = 3):
        plot_num = 0
        stock_list = get_random_stock_code_and_name_list(stock_num=stock_num)
        for stock in stock_list:
            if plot_num < max_plot_num:
                self.add_stock(stock[0], stock[1])
                plot_num += 1
            else:
                self.add_stock(stock[0], stock[1])

    def using_csv_pool(self, file_path: str, sheet_name: str = "Sheet1", code_id: int = 0, name_id: int = 1):
        """
        读取本地csv文件，获取其中的股票池，作为选股范围
        """
        # 打开Excel文件, 选择要操作的工作表
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook[sheet_name]

        # 获取列名为"代码"的单元格数据
        code_column = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            code = row[code_id]  # 假设"代码"列是第一列，索引从0开始
            name = row[name_id]  # 假设"代码"列是第一列，索引从0开始
            if code is not None and name is not None:
                stock_code = str(code)[2:]
                stock_name = str(name)
                self.add_stock(stock_code, stock_name)
                # self.add_stock_by_code(stock_code)

    def use_all_code(self, start_time: str = "20230801"):
        # my_time = pd.to_datetime(start_time, format='%Y%m%d')
        # data = time_utils.tushare_api().stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,list_status,list_date')
        # for index, row in data.iterrows():
        #     if my_time > pd.to_datetime(row['list_date'], format='%Y%m%d'):
        #         self.add_stock(row['symbol'], row['name'])
        # 这里20241112对数据获取接口进行了改造，去除了tushare的依赖
        self.temp_result = get_basic_data_info(start_time)
        for stock in self.temp_result:
            self.add_stock(stock)

    def add_stock(self, stock_info: dict):
        stock = Stock(stock_code=stock_info['股票代码'],
                      stock_code_ts=get_total_stock_code(stock_info['股票代码']),
                      stock_name=stock_info['股票名称'],
                      market=stock_info['市场'],
                      ipo_date_str=stock_info['上市日期']
        )
        stock.basic_info = stock_info
        print(stock.basic_info)
        stock.init_max_and_min_price()
        stock.position.static_tp_ratio = config.STATIC_TP_RATIO  # 止盈率
        stock.position.static_sl_ratio = config.STATIC_SL_RATIO  # 止损率
        self.all_stock.append(stock)

    def add_stock_by_code(self, stock_code: str):
        """
        速度较慢，待优化
        """

        df = time_utils.tushare_api().stock_basic(exchange='',
                                                  list_status='L',  # 上市状态 L上市 D退市 P暂停上市，默认是L
                                                  fields='ts_code,symbol,name')
        stock_info = df.loc[df['cc'] == stock_code]
        stock_name = stock_info['name'].values[0] if not stock_info.empty else "Stock not found"
        stock = Stock(stock_code=stock_code,
                      stock_code_ts=get_total_stock_code(stock_code),
                      stock_name=stock_name)
        self.all_stock.append(stock)
        return stock

    def add_position(self, stock_code: str, buy_price: float, buy_size: float, position_date: str):
        for stock in self.all_stock:
            if stock.stock_code == stock_code:
                stock.position.buy_action(buy_price=buy_price, buy_size=buy_size, position_date=position_date)
                break

    def start_log(self, log):
        log.log(f"【已创建{self.my_stock_num}只股票的股票池, 回测日期: 从 {self.start_date} ~ {self.now_date}】")
        # log.log(f"包含: {self.all_stock_info}")
        print(f"包含: {self.all_stock_info}")

    def strategy_log(self, log):
        expect_buy_stocks = [stock for stock in self.all_stock if stock.buy_trigger.today_meet and not stock.buy_trigger.already_execute]
        expect_buy_stocks_with_size = [stock for stock in self.all_stock if stock.buy_trigger.expect_buy_size > 0]

        log.log(f"\n【共检测到 {len(expect_buy_stocks)} 只触发买入条件股，生成 {len(expect_buy_stocks_with_size)} 条买入策略】")
        for stock in expect_buy_stocks:
            log.log(stock.log_tick)
            log.log(stock.log_buy_strategy)

        expect_sell_stocks = [stock for stock in self.all_stock if stock.sell_trigger.today_meet and not stock.sell_trigger.already_execute]
        log.log(f"【共检测到 {len(expect_sell_stocks)} 只触发卖出条件，并生成卖出策略】")
        for stock in expect_sell_stocks:
            log.log(stock.log_tick)
            log.log(stock.log_sell_strategy)



