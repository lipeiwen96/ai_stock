"""
主程序
"""
from dataclasses import field, dataclass
from datetime import datetime
from stock_sentinel.stock_pool_v2 import StockPool
from stock_sentinel import crawler_v2
import time
from pathlib import Path
import os


@dataclass
class StockSelector:
    stock_pool: StockPool = field(default_factory=StockPool)
    last_dict: dict = field(default=dict)  # 历史数据

    def init_stock_pool(self, from_date):
        """初始化股票池"""
        self.stock_pool = StockPool()
        self.stock_pool.init_time(start_date=from_date.strftime('%Y-%m-%d'))
        self.stock_pool.use_all_code(start_time=from_date.strftime('%Y%m%d'))  # 使用全盘股票
        print(f"包含: {self.stock_pool.all_stock_info}")

        # 获取股票代码列表
        self.scode_list = [stock.stock_code for stock in self.stock_pool.all_stock]
        self.scode_list.insert(0, "1.000001")
        # print(self.scode_list)
        self.stock_pool.szzz.stock_code = "1.000001"
        self.stock_pool.szzz.stock_name = "上证综指"

    def add_cache(self, from_date):
        """
        缓存历史日线数据，淘宝写的，用这个来计算历史的数据，存至data/文件夹
        """
        trade_day_list = crawler_v2.get_current_trade_day()
        yesterday, today = trade_day_list[-2:]
        print(f"- 时间校验，昨天日期为: {yesterday}, 今天日期为: {today}；当前时刻: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")

        if not os.path.exists("data"):
            os.mkdir("data")

        # 缓存机制
        kline_file = Path(f"data/{today}.pkl")

        # 检查是否存在今日的缓存文件
        if kline_file.exists():
            self.last_dict = crawler_v2.load_cached_data(kline_file)
            print("【历史数据已从今日缓存中加载】")
        else:
            # 删除旧的缓存文件
            for file in Path("data").glob("*.pkl"):
                file.unlink()

            # 重新计算并缓存
            self.last_dict = crawler_v2.get_last_data(self.scode_list, kline_file, from_date.strftime('%Y-%m-%d'))
            print("【历史数据重新计算并缓存】")

    def renew_tick(self):
        """
        通用Tick数据刷新接口
        """
        # 更新时刻
        start_time = time.time()
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 更新最新Tick数据
        data_list = []
        data_list = crawler_v2.get_hs_data(self.last_dict, self.scode_list)
        if len(data_list) != 0:
            for item in data_list:
                if item["股票代码"] == "1.000001":
                    # print(item)
                    self.stock_pool.szzz.tick.renew(item=item)
                else:
                    index = self.scode_list.index(item["股票代码"]) - 1
                    if item["最新价"] == "-":
                        print(f"--- {self.stock_pool.all_stock[index].log_name} 当前停盘，无法获取数据")
                        continue
                    stock = self.stock_pool.all_stock[index]
                    # print(item)
                    stock.tick.renew(item=item)

    def filter_stocks(self, conditions):
        """根据条件筛选股票"""
        filtered_stocks = []

        for stock in self.stock_pool.all_stock:
            meet_all_conditions = True

            for condition in conditions:
                if condition["enabled"]:
                    if condition["type"] == "PRICE_ABOVE_EMA5":
                        if not (stock.tick.price > stock.tick.ema_5):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_BELOW_EMA5":
                        if not (stock.tick.price < stock.tick.ema_5 * (1 + float(condition["percentage"]))):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_ABOVE_EMA13":
                        if not (stock.tick.price > stock.tick.ema_13):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_BELOW_EMA13":
                        if not (stock.tick.price < stock.tick.ema_13 * (1 + float(condition["percentage"]))):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_ABOVE_EMA30":
                        if not (stock.tick.price > stock.tick.ema_30):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_BELOW_EMA30":
                        if not (stock.tick.price < stock.tick.ema_30 * (1 + float(condition["percentage"]))):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_ABOVE_EMA60":
                        if not (stock.tick.price > stock.tick.ema_60):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_BELOW_EMA60":
                        if not (stock.tick.price < stock.tick.ema_60 * (1 + float(condition["percentage"]))):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_ABOVE_MA100":
                        if not (stock.tick.price > stock.tick.ma_100):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "PRICE_BELOW_MA100":
                        if not (stock.tick.price < stock.tick.ma_100 * (1 + float(condition["percentage"]))):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "EMA13_ABOVE_EMA30":
                        if not (stock.tick.ema_13 > stock.tick.ema_30):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "EMA13_ABOVE_EMA60":
                        if not (stock.tick.ema_13 > stock.tick.ema_60):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "EMA13_ABOVE_MA100":
                        if not (stock.tick.ema_13 > stock.tick.ma_100):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "EMA30_ABOVE_EMA60":
                        if not (stock.tick.ema_30 > stock.tick.ema_60):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "EMA60_ABOVE_MA100":
                        if not (stock.tick.ema_60 > stock.tick.ma_100):
                            meet_all_conditions = False
                            break
                    elif condition["type"] == "EMA13_CROSS_EMA18":
                        if not stock.tick.ema_13_cross_ema_18:
                            meet_all_conditions = False
                            break

            if meet_all_conditions:
                filtered_stocks.append(stock)

        return filtered_stocks
