"""
股票池
"""
from dataclasses import field, dataclass
from typing import List
import pandas as pd
import openpyxl

import config
from utils import time_utils

from stock_sentinel.stock_v2 import Stock
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
        temp_result = get_basic_data_info(start_time)
        # print(temp_result)
        for stock in temp_result:
            self.add_stock(stock)

    def add_stock(self, stock_info: dict):
        stock = Stock(stock_code=stock_info['股票代码'],
                      stock_code_ts=get_total_stock_code(stock_info['股票代码']),
                      stock_name=stock_info['股票名称'],
                      )
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


