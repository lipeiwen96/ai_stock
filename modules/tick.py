from dataclasses import field, dataclass
from typing import List
from utils.log_utils import v_round


@dataclass
class Tick:
    price: float = field(default=0.000)  # 当前价格
    increase_rate: float = field(default=0.000)  # 当前价格相对于昨日收盘价
    open: float = field(default=0.000)
    close: float = field(default=0.000)  # TODO: 暂未接入
    high: float = field(default=0.000)
    low: float = field(default=0.000)

    ma_3: float = field(default=0.000)
    ma_5: float = field(default=0.000)
    ma_7: float = field(default=0.000)
    ma_10: float = field(default=0.000)
    ma_12: float = field(default=0.000)
    ma_20: float = field(default=0.000)
    ma_30: float = field(default=0.000)
    macd: float = field(default=0.000)
    macd_yesterday: float = field(default=0.000)
    ma3_yesterday: float = field(default=0.000)
    ma5_yesterday: float = field(default=0.000)
    ma7_yesterday: float = field(default=0.000)
    ma10_yesterday: float = field(default=0.000)
    ma12_yesterday: float = field(default=0.000)
    ma20_yesterday: float = field(default=0.000)
    ma5_before: float = field(default=0.000)
    ma10_before: float = field(default=0.000)

    # ma_5与ma_10的大小关系
    ma5_larger_than_ma10: bool = field(default=False)
    ma5_cross_ma10: bool = field(default=False)
    form_signal: bool = field(default=False)  # 金叉预备式

    ma3_up_cross_ma7: bool = field(default=False)
    ma3_down_cross_ma5: bool = field(default=False)

    @property
    def is_golden_cross(self):
        """
        判断股票是否为金叉状态
        """
        if self.ma5_cross_ma10 > 0:
            return True
        else:
            return False

    @property
    def is_macd_meet(self):
        """
        判断股票MACD是否为红
        """
        if self.macd > 0 or self.macd >= self.macd_yesterday:
            return True
        else:
            return False

    @property
    def is_golden_cross_over_ma20(self):
        """
        短线均线需要超过长期均线
        """
        if self.ma_5 >= self.ma_20 and self.ma_10 >= self.ma_20:
            return True
        else:
            return False

    def renew(self, item: dict, total_beat_id: int):
        self.price = item["最新价"]
        self.open = item["开盘价"] if item["开盘价"] != "-" else 0.000
        self.high = item["最高价"] if item["最高价"] != "-" else 0.000
        self.low = item["最低价"] if item["最低价"] != "-" else 0.000

        self.ma_3 = item["MA3"] if item["MA3"] != "-" else 0.000
        self.ma_5 = item["MA5"] if item["MA5"] != "-" else 0.000
        self.ma_7 = item["MA7"] if item["MA7"] != "-" else 0.000
        self.ma_10 = item["MA10"] if item["MA10"] != "-" else 0.000
        self.ma_12 = item["MA12"] if item["MA12"] != "-" else 0.000
        self.ma5_larger_than_ma10 = True if self.ma_5 > self.ma_10 else False
        self.ma_20 = item["MA20"] if item["MA20"] != "-" else 0.000
        self.ma_30 = item["MA30"] if item["MA30"] != "-" else 0.000
        self.macd = item["MACD_today"] if item["MACD_today"] != "-" else 0.000
        self.macd_yesterday = item["MACD_yesterday"] if item["MACD_yesterday"] != "-" else 0.000

        self.ma3_yesterday = item["ma3_yesterday"] if item["ma3_yesterday"] != "-" else 0.000
        self.ma5_yesterday = item["ma5_yesterday"] if item["ma5_yesterday"] != "-" else 0.000
        self.ma7_yesterday = item["ma7_yesterday"] if item["ma7_yesterday"] != "-" else 0.000
        self.ma10_yesterday = item["ma10_yesterday"] if item["ma10_yesterday"] != "-" else 0.000
        self.ma12_yesterday = item["ma12_yesterday"] if item["ma12_yesterday"] != "-" else 0.000
        self.ma20_yesterday = item["ma20_yesterday"] if item["ma20_yesterday"] != "-" else 0.000
        self.ma5_before = item["ma5_before"] if item["ma5_before"] != "-" else 0.000
        self.ma10_before = item["ma10_before"] if item["ma10_before"] != "-" else 0.000

        if total_beat_id == 0:
            # 仅在第一次初始化的指标
            if self.ma5_yesterday < self.ma10_yesterday:
                # 有形成金叉的趋势
                self.form_signal = True
            else:
                self.form_signal = False

        if self.form_signal and self.ma5_larger_than_ma10 and self.ma_5 > self.ma5_yesterday:
            self.ma5_cross_ma10 = True
        else:
            self.ma5_cross_ma10 = False

        if self.ma_3 > self.ma_7 and self.ma3_yesterday <= self.ma7_yesterday and self.ma_3 > self.ma3_yesterday:
        # if self.ma_3 > self.ma_7 and self.ma3_yesterday <= self.ma7_yesterday:
            # MA3 上传 MA7 形成金叉
            self.ma3_up_cross_ma7 = True
        else:
            self.ma3_up_cross_ma7 = False

        # if self.ma_3 < self.ma_5 and self.ma3_yesterday >= self.ma5_yesterday and self.ma_3 < self.ma3_yesterday:
        if self.ma_3 < self.ma_5:
            # MA3 下传 MA5 形成死叉
            self.ma3_down_cross_ma5 = True
        else:
            self.ma3_down_cross_ma5 = False

    @property
    def log(self):
        return f"-[股价]当前价格: {v_round(self.price)}元, 当日开盘价: {v_round(self.open)}元, " \
               f"股价范围:{v_round(self.low)} ~ {v_round(self.high)}元;<br>\n" \
               f"-[指标]当前MACD: {v_round(self.macd)}, 昨日MACD: {v_round(self.macd_yesterday)}, {'收敛' if self.macd >= self.macd_yesterday else '' }， " \
               f"当前MA3:{v_round(self.ma_3)}元 【{'>' if self.ma_3 > self.ma3_yesterday else '<='}】昨日MA3:{v_round(self.ma3_yesterday)}元; " \
               f"当前MA5:{v_round(self.ma_5)}元 【{'>' if self.ma_5 > self.ma5_yesterday else '<='}】昨日MA5:{v_round(self.ma5_yesterday)}元; " \
               f"当前MA7:{v_round(self.ma_7)}元 【{'>' if self.ma_7 > self.ma7_yesterday else '<='}】昨日MA7:{v_round(self.ma7_yesterday)}元; " \
               f"当前MA10:{v_round(self.ma_10)}元 【{'>' if self.ma_10 > self.ma10_yesterday else '<='}】昨日MA10:{v_round(self.ma10_yesterday)}元; " \
               f"当前MA12:{v_round(self.ma_12)}元 【{'>' if self.ma_12 > self.ma12_yesterday else '<='}】昨日MA12:{v_round(self.ma12_yesterday)}元; " \
               f"当前MA20:{v_round(self.ma_20)}元 【{'>' if self.ma_20 > self.ma20_yesterday else '<='}】昨日MA20:{v_round(self.ma20_yesterday)}元; " \
               f"{'当日 MA3 上传 MA7 形成【金叉】' if self.ma3_up_cross_ma7 else ''}" \
               f"{'当日 MA3 下传 MA5 形成【死叉】' if self.ma3_down_cross_ma5 else ''}"

