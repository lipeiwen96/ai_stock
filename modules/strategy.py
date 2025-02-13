"""
策略主脑
"""
from dataclasses import field, dataclass
from typing import List
import math
import config

from modules.stock import Stock
from modules.stock_pool import StockPool
from modules.account import Account
from utils.math_utils import robust_divide


def unitization(num: float):
    """
    遵循国内市场的最小交易单位规定：将任意数额的买入份额变成一百手的整数倍
    """
    return math.floor(num / 100) * 100


def compute_buy_size(expect_price):
    expect_buy_size = unitization(robust_divide(config.EXPECT_VALUE, expect_price))  # 看看指定额度最多买多少股

    if expect_buy_size < 100:
        expect_buy_size = 0  # 最少买入200股
    elif expect_buy_size < 200:
        if (expect_buy_size + 100) * expect_price > config.MAX_VALUE:
            expect_buy_size = 0
        else:
            expect_buy_size = 200
    else:
        # 新增 尽可能接近2w，上下限1.5-2.5w
        compute_above = True
        compute_double_above = True
        compute_below = True
        if (expect_buy_size + 100) * expect_price > config.MAX_VALUE:
            compute_above = False
        if (expect_buy_size + 200) * expect_price > config.MAX_VALUE:
            compute_double_above = False
        if (expect_buy_size - 100) * expect_price < config.MIN_VALUE:
            compute_below = False

        if not compute_above and not compute_below and not compute_double_above:
            pass
        else:
            dif_list = [abs(expect_buy_size * expect_price - config.EXPECT_VALUE),
                        abs((expect_buy_size + 100) * expect_price - config.EXPECT_VALUE) if compute_above else 999999,
                        abs((expect_buy_size + 200) * expect_price - config.EXPECT_VALUE) if compute_double_above else 999999,
                        abs((expect_buy_size - 100) * expect_price - config.EXPECT_VALUE) if compute_below else 999999]
            min_dif_id = dif_list.index(min(dif_list))
            if min_dif_id == 0:
                pass
            elif min_dif_id == 1:
                expect_buy_size += 100
            elif min_dif_id == 2:
                expect_buy_size += 200
            else:
                expect_buy_size -= 100
                expect_buy_size = max(expect_buy_size, 200)

    return expect_buy_size


@dataclass
class Strategy:

    @staticmethod
    def execute_strategy(now: str, stock_pool: StockPool, account: Account, log):
        """
        执行判断策略
        -> 转化为trigger的状态变化
        """
        # if stock_pool.szzz.tick.price > stock_pool.szzz.tick.ma_20:
        #     config.STATIC_TP_RATIO = 0.01
        # else:
        #     config.STATIC_TP_RATIO = 0.01
        # for stock in stock_pool.all_stock:
        #     stock.position.static_tp_ratio = config.STATIC_TP_RATIO

        log.log(f"【当前时刻上证指数价格: {round(stock_pool.szzz.tick.price, 3)} "
                f"{'>' if stock_pool.szzz.tick.price > stock_pool.szzz.tick.ma_20 else '<='} 当日MA20: {round(stock_pool.szzz.tick.ma_20, 3)}, "
                f"{'形式较好' if stock_pool.szzz.tick.price > stock_pool.szzz.tick.ma_20 else '形式较差'},  --> 止盈率设置为 {config.STATIC_TP_RATIO}】")

        for stock in stock_pool.all_stock:
            if stock.position.has_position:
                if stock.tick.price < 0.01:
                    # 等有数据再刷新
                    continue
                if stock.position.can_use_size > 0:
                    """
                    卖出判定策略
                    """
                    Strategy.execute_sell_strategy(stock, log)
                    pass
                else:
                    # 今日卖出的股票，不再予以买入
                    # 当日买入订单，不执行操作
                    continue
            else:
                """
                买入判断策略
                """
                if stock.tick.price < 0.01:
                    # 等有数据再刷新
                    continue
                Strategy.execute_buy_strategy(stock, log)
                pass

        # 通用计算买入量
        # Strategy.normal_compute_buy_value(now, stock_pool, account)

        # 20231119 固定限额买入股票
        Strategy.limit_value_compute(now, stock_pool, account, log)

    @staticmethod
    def limit_value_compute(now: str, stock_pool: StockPool, account: Account, log):
        """
        以固定限额，买入股票
        """
        # 按照触发次数排序
        buy_trigger_stocks = [stock for stock in stock_pool.all_stock if stock.buy_trigger.today_meet and
                              not stock.buy_trigger.already_execute]

        if len(buy_trigger_stocks) > 0:
            available_cash = account.can_use_cash

            if available_cash >= config.MIN_VALUE:
                # 从最大金额开始排序
                buy_trigger_stocks = sorted(buy_trigger_stocks, key=lambda x: x.buy_trigger.expect_price, reverse=True)  # 降序排列
                buy_status = False

                # 从高往低排序买入
                for stock in buy_trigger_stocks:
                    expect_buy_size = compute_buy_size(stock.buy_trigger.expect_price)
                    if expect_buy_size == 0:
                        stock.buy_trigger.expect_buy_size = 0
                        log.log(f"{now}, - 当前时刻账面可用资金{round(available_cash, 2)}元, 不足以买入 {stock.log_name}-{round(stock.buy_trigger.expect_price * (1 + config.COMMISSION_RATE) * expect_buy_size, 2)}元的份额...")
                    else:
                        # 看看当前资金能否买入
                        if available_cash > stock.buy_trigger.expect_price * (1 + config.COMMISSION_RATE) * expect_buy_size:
                            # 能够买入
                            buy_status = True
                            stock.buy_trigger.expect_buy_size = expect_buy_size
                            log.log(f"{now}, - 【单股买入计算成功】，{stock.log_name}, 买入量为: {expect_buy_size}")
                            available_cash -= stock.buy_trigger.expect_price * (1 + config.COMMISSION_RATE) * expect_buy_size
                        else:
                            stock.buy_trigger.expect_buy_size = 0
                            log.log(f"{now}, - 当前时刻账面可用资金{round(available_cash, 2)}元, 不足以买入 {stock.log_name}-{round(stock.buy_trigger.expect_price * (1 + config.COMMISSION_RATE) * expect_buy_size, 2)}元的份额...")

            else:
                log.log(f"{now}, 当前时刻账面可用资金{round(available_cash, 2)}元, 不足以买入最少限额: {config.MIN_VALUE}元的股票...")
        else:
            log.log(f"{now}, 当前时刻无买入操作...")

    @staticmethod
    def normal_compute_buy_value(now: str, stock_pool: StockPool, account: Account):
        # 按照触发次数排序
        buy_trigger_stocks = [stock for stock in stock_pool.all_stock if stock.buy_trigger.today_meet and
                              not stock.buy_trigger.already_execute]
        # print(buy_trigger_stocks)

        if len(buy_trigger_stocks) > 0:
            buy_trigger_stocks = sorted(buy_trigger_stocks, key=lambda x: x.buy_trigger.trigger_times, reverse=True)
            max_buy_price_list = [stock.buy_trigger.expect_max_price for stock in buy_trigger_stocks]
            total_price = sum(max_buy_price_list)

            available_cash = account.can_use_cash

            if available_cash < min(max_buy_price_list) * config.MIN_BUY_PRICE:
                print(f"{now}, 当前时刻账面可用资金{available_cash}元, 不足下单...")
            else:
                # 计算平均买入量
                expect_size = unitization(robust_divide(available_cash, total_price))
                print(f"{now}, - 尝试整体买入，平均买入份额为: {expect_size}")

                if expect_size >= config.MIN_BUY_PRICE:
                    # 判断1：单股是否超过最高持仓仓位占比

                    for stock in buy_trigger_stocks:
                        if stock.buy_trigger.expect_max_price * expect_size >= account.single_stock_max_buy_value:
                            # 调整买入量
                            scale_ratio = robust_divide(account.single_stock_max_buy_value, stock.buy_trigger.expect_max_price * expect_size)
                            expect_size_revised = unitization(expect_size * scale_ratio)
                            stock.buy_trigger.expect_buy_size = expect_size_revised
                            print(f"{now}, - 单股买入量调整，{stock.log_name}调整后买入量为: {expect_size_revised}")
                        else:
                            stock.buy_trigger.expect_buy_size = expect_size

                else:
                    print(f"{now}, - 整体买入份额过少，尝试调整策略为逐个买入...")
                    # 判断2：买入量份额过少，尝试逐个股票买入
                    buy_status = False
                    remaining_cash = available_cash

                    for stock in buy_trigger_stocks:
                        if remaining_cash >= stock.buy_trigger.expect_max_price * config.MIN_BUY_PRICE:
                            stock.buy_trigger.expect_buy_size = unitization(robust_divide(remaining_cash, stock.buy_trigger.expect_max_price))
                            print(f"{now}, - 策略调整，变为逐个买入，{stock.log_name}的买入量为: {stock.buy_trigger.expect_buy_size}")
                            remaining_cash -= stock.buy_trigger.expect_max_price * stock.buy_trigger.expect_buy_size * (1 + config.COMMISSION_RATE)
                            buy_status = True

                    if not buy_status:
                        print(f"{now}, - 逐个买入失败，当前时刻账面可用资金{available_cash}元, 不足下单...")

        else:
            print(f"{now}, 当前时刻无买入操作...")

    @staticmethod
    def execute_buy_strategy(stock: Stock, log):
        """
        买入判断策略
        """
        # if stock.tick.is_golden_cross and stock.tick.is_macd_red and stock.tick.is_golden_cross_over_ma20:
        if stock.tick.ma3_up_cross_ma7 and stock.tick.is_macd_meet:
            # 现价买入
            price_info = "金叉信号，现价买"
            buy_price = stock.tick.price

            # # 稍微稳妥一些，看能不能以金叉价买入
            # if stock.tick.ma_10 < stock.tick.low:
            #     # 强势涨
            #     price_info = "现价"
            #     buy_price = stock.tick.price
            # elif stock.tick.price < stock.tick.ma_10:
            #     # 强势涨
            #     price_info = "现价"
            #     buy_price = stock.tick.price
            # else:
            #     price_info = "金叉价"
            #     buy_price = stock.tick.ma_10

            log.log(f"[{stock.log_name}]股触发【买信号】，买入点为[{price_info}]: {round(buy_price, 3)}元")
            stock.buy_trigger.add_trigger(stock.tick.price, price_info)

    @staticmethod
    def execute_sell_strategy(stock: Stock, log):
        """
        卖出判定策略
        """
        # TODO: 动态止盈暂时无法实现，需要解决建仓时间问题
        if stock.tick.ma3_down_cross_ma5:
            """
            触发死叉卖出
            """
            price_info = "死叉信号，现价卖"
            stock.sell_trigger.add_trigger(stock.tick.price, price_info)
            stock.sell_trigger.is_TP = False

        # if stock.tick.price < stock.tick.ma_20:
        #     """
        #     跌破20日线
        #     """
        #     price_info = "MA20"
        #     stock.sell_trigger.add_trigger(stock.tick.price, price_info)
        #     stock.sell_trigger.is_TP = False

        if stock.tick.price < stock.position.static_SL_price:
            """2
3
            .i静态止跌5个点
            """
            price_info = "5%静态止跌，现价卖"
            stock.sell_trigger.add_trigger(stock.tick.price, price_info)
            stock.sell_trigger.is_TP = False

        if stock.tick.price >= stock.position.static_TP_price:
            """
            静态止盈16个点
            """
            price_info = "10%静态止盈价，现价卖"
            stock.sell_trigger.add_trigger(stock.tick.price, price_info)
            stock.sell_trigger.is_TP = True

        # elif stock.tick.price <= stock.position.dynamic_TP_price:
        #     """
        #     动态止盈-0.66
        #     """
        #     price_info = "动态止盈价"
        #     stock.sell_trigger.add_trigger(stock.tick.price, price_info)
        #     stock.sell_trigger.is_TP = True
        if stock.sell_trigger.today_meet:
            log.log(f"[{stock.log_name}]股触发【卖信号】，卖出点为[{stock.sell_trigger.price_info}]: {round(stock.sell_trigger.expect_price, 3)}元")

            benefit = stock.sell_trigger.expect_price - stock.position.buy_price
            benefit_ratio = round(abs(robust_divide(benefit, stock.position.buy_price)), 4)
            log.log(f" - {'[止盈]' if benefit >= 0 else '[止跌]'} {round(benefit_ratio * 100, 2)}%")

