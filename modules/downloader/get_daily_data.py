"""
TUSHARE 获取日级数据
"""
import tushare as ts
import pandas as pd


def get_daily_data(trade_date_range, code: str = "600519", start_time: str = "2021-01-01", end_time: str = "2024-01-01",
                   fillna: bool = True):
    """
    这里调用tushare基础班的接口，对pandas版本有要求
    -- pip install pandas==1.3.5
    """

    df = ts.get_k_data(code, start=start_time, end=end_time)
    # 把索引设置为日期格式
    df.index = pd.to_datetime(df.date)
    # 补充OpenInterest数据格式
    df["openinterest"] = 0
    # 对df数据列进行整合
    df = df[["open", "high", "low", "close", "volume", "openinterest"]]  # 指定顺序

    # 数据的自动补全，
    if not df.empty and fillna:
        # 补全缺失的日期数据
        # date_range = pd.date_range(start=start_time, end=end_time, freq='B')
        # print(date_range)
        df = df.reindex(trade_date_range)

        # 填充缺失的数据
        df['code'] = code
        df['date'] = df.index.strftime('%Y-%m-%d')
        # 使用前向填充和后向填充来插值
        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)

    return df