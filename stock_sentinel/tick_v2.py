from dataclasses import field, dataclass
from utils.log_utils import v_round


@dataclass
class Tick:
    price: float = field(default=0.000)  # 当前价格
    increase_rate: float = field(default=0.000)  # 当前价格相对于昨日收盘价
    open: float = field(default=0.000)
    close: float = field(default=0.000)  # TODO: 暂未接入
    high: float = field(default=0.000)
    low: float = field(default=0.000)
    market: str = field(default=str)

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

    ema_5: float = field(default=0.000)
    ema_13: float = field(default=0.000)
    ema_18: float = field(default=0.000)
    ema_13_cross_ema_18: bool = field(default=False)
    ema_30: float = field(default=0.000)
    ema_60: float = field(default=0.000)
    ma_60: float = field(default=0.000)
    ma_100: float = field(default=0.000)

    def renew(self, item: dict):
        self.price = item["最新价"]
        self.open = item["开盘价"] if item["开盘价"] != "-" else 0.000
        self.high = item["最高价"] if item["最高价"] != "-" else 0.000
        self.low = item["最低价"] if item["最低价"] != "-" else 0.000
        self.market = item["市场"]

        self.ma_3 = item["MA3"] if item["MA3"] != "-" else 0.000
        self.ma_5 = item["MA5"] if item["MA5"] != "-" else 0.000
        self.ma_7 = item["MA7"] if item["MA7"] != "-" else 0.000
        self.ma_10 = item["MA10"] if item["MA10"] != "-" else 0.000
        self.ma_12 = item["MA12"] if item["MA12"] != "-" else 0.000
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

        # 'EMA5': 3279.01, 'EMA13': 3258.86, 'EMA30': 3161.76, 'EMA60': 3069.05,'MA60': 2982.98, 'MA100': 2979.24
        self.ema_5 = item["EMA5"] if item["EMA5"] != "-" else 0.000
        self.ema_13 = item["EMA13"] if item["EMA13"] != "-" else 0.000
        self.ema_18 = item["EMA18"] if item["EMA18"] != "-" else 0.000
        self.ema_13_cross_ema_18 = bool(item["EMA13_上穿_EMA18"]) if item["EMA13_上穿_EMA18"] != "-" else False
        self.ema_30 = item["EMA30"] if item["EMA30"] != "-" else 0.000
        self.ema_60 = item["EMA60"] if item["EMA60"] != "-" else 0.000
        self.ma_60 = item["MA60"] if item["MA60"] != "-" else 0.000
        self.ma_100 = item["MA100"] if item["MA100"] != "-" else 0.000

    @property
    def log(self):
        return f"-[股价]当前价格: {v_round(self.price)}元, 当日开盘价: {v_round(self.open)}元, " \
               f"当日股价最低:{v_round(self.low)} ~ 最高:{v_round(self.high)}元;<br>\n" \
               f"-[MACD]当前MACD: {v_round(self.macd)}, 昨日MACD: {v_round(self.macd_yesterday)}, {'收敛' if self.macd >= self.macd_yesterday else '' }\n" \
               f"-[MA]当前MA3:{v_round(self.ma_3)}元; " \
               f"当前MA5:{v_round(self.ma_5)}元; " \
               f"当前MA7:{v_round(self.ma_7)}元; " \
               f"当前MA10:{v_round(self.ma_10)}元; " \
               f"当前MA12:{v_round(self.ma_12)}元; " \
               f"当前MA20:{v_round(self.ma_20)}元; " \
               f"当前MA30:{v_round(self.ma_30)}元; " \
               f"当前MA60:{v_round(self.ma_60)}元; " \
               f"当前MA100:{v_round(self.ma_100)}元; " \
               f"-[EMA]当前EMA5:{v_round(self.ema_5)}元; " \
               f"当前EMA13:{v_round(self.ema_13)}元; " \
               f"当前EMA18:{v_round(self.ema_18)}元; " \
               f"当前EMA13{'【上穿】' if self.ema_13_cross_ema_18 else '未上穿'}EMA18; " \
               f"当前EMA30:{v_round(self.ema_30)}元; " \
               f"当前EMA60:{v_round(self.ema_60)}元; "
