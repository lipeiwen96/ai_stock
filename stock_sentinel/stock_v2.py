"""
单只股票的基础结构
"""
from dataclasses import field, dataclass
from stock_sentinel.tick_v2 import Tick


@dataclass
class Stock:
    stock_code: str = field(default="000001")
    stock_code_ts: str = field(default="000001.SZ")
    stock_name: str = field(default="")

    # 实盘数据及指标数据
    tick: Tick = field(default_factory=Tick)

    @property
    def log_name(self):
        return "|" + self.stock_code + "." + self.stock_name + "|"

    @property
    def log_tick(self):
        return self.log_name + "<br>\n" + self.tick.log
