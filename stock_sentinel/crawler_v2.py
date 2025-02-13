"""
淘宝写的实盘数据爬取接口
对应1.2.4 实盘秒级数据获取接口
"""

import pandas as pd
import time
import requests
import pickle
from multiprocessing import pool


def Requests(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edg/89.0.774.50'}):
    error_time = 0
    while True:
        try:
            r = requests.get(url, headers=headers, timeout=3)
            return r
        except:
            error_time += 1
            time.sleep(1)
            if error_time > 5:
                return requests.Response()


def get_macd_ma(Close, Open, High, Low,
                last_dict={"dea": 0, "ema12": 0, "ema13": 0, "ema18": 0,"ema26": 0, "ma29": 0, "sum4": 0, "sum9": 0, "sum29": 0, "sum59": 0}):
    # 计算MACD
    try:
        ema12 = last_dict["ema12"] * 11 / 13 + Close * 2 / 13
        ema26 = last_dict["ema26"] * 25 / 27 + Close * 2 / 27
        dif = round(ema12 - ema26, 4)
        dea = round(last_dict["dea"] * 8 / 10 + dif * 2 / 10, 4)
        macd = round((dif - dea) * 2, 4)
        ma5 = round(sum(last_dict["sum4"] + [Close]) / (len(last_dict["sum4"]) + 1), 2)
        ma10 = round(sum(last_dict["sum9"] + [Close]) / (len(last_dict["sum9"]) + 1), 2)
        ma20 = round(sum(last_dict["sum19"] + [Close]) / (len(last_dict["sum19"]) + 1), 2)
        ma30 = round(sum(last_dict["sum29"] + [Close]) / (len(last_dict["sum29"]) + 1), 2)
        ma60 = round(sum(last_dict["sum59"] + [Close]) / (len(last_dict["sum59"]) + 1), 2)
        ma100 = round(sum(last_dict["sum99"] + [Close]) / (len(last_dict["sum99"]) + 1), 2)

        ma3 = round(sum(last_dict["sum2"] + [Close]) / (len(last_dict["sum2"]) + 1), 2)
        ma7 = round(sum(last_dict["sum6"] + [Close]) / (len(last_dict["sum6"]) + 1), 2)
        ma12 = round(sum(last_dict["sum11"] + [Close]) / (len(last_dict["sum11"]) + 1), 2)

        # Calculate EMAs
        ema5 = last_dict["ema5"] * 4/6 + Close * 2/6 if "ema5" in last_dict else Close
        ema13 = last_dict["ema13"] * 12/14 + Close * 2/14 if "ema13" in last_dict else Close
        ema30 = last_dict["ema30"] * 29/31 + Close * 2/31 if "ema30" in last_dict else Close
        ema60 = last_dict["ema60"] * 59/61 + Close * 2/61 if "ema60" in last_dict else Close
        # +++ 新增EMA18计算 +++
        ema18 = last_dict["ema18"] * 17 / 19 + Close * 2 / 19 if "ema18" in last_dict else Close
        # +++ 新增上穿判断 +++
        # 获取昨日EMA值
        ema13_yesterday = last_dict["ema13"]
        ema18_yesterday = last_dict["ema18"]
        # 计算上穿条件
        cross_over = (ema13 > ema18) and (ema13_yesterday <= ema18_yesterday) and (ema13 > ema13_yesterday)

        ochl_list = []
        for value, (h, l) in zip((Open, Close, High, Low), last_dict["OCHL"]):
            ochl_list.append(max(value, h))
            ochl_list.append(min(value, l))
        开盘价_最大值, 开盘价_最小值, 收盘价_最大值, 收盘价_最小值, 最高价_最大值, 最高价_最小值, 最低价_最大值, 最低价_最小值 = ochl_list

        return {"DIF": dif, "DEA": dea, "MA30": ma30, "MACD_today": macd, "MACD_yesterday": last_dict["MACD_yesterday"],
                "MA5": ma5, "MA10": ma10, "MA20": ma20, "MA30": ma30, "MA60": ma60, "MA100": ma100,
                "MA3": ma3, "MA7": ma7, "MA12": ma12,
                "EMA5": round(ema5, 2),
                "EMA13": round(ema13, 2),
                "EMA18": round(ema18, 2),
                "EMA13_上穿_EMA18": cross_over,
                "EMA30": round(ema30, 2),
                "EMA60": round(ema60, 2),
                "ma5_yesterday": last_dict["ma5_yesterday"],
                "ma10_yesterday": last_dict["ma10_yesterday"],
                "ma20_yesterday": last_dict["ma20_yesterday"],

                "ma3_yesterday": last_dict["ma3_yesterday"],
                "ma7_yesterday": last_dict["ma7_yesterday"],
                "ma12_yesterday": last_dict["ma12_yesterday"],

                "ma5_before": last_dict["ma5_before"],
                "ma10_before": last_dict["ma10_before"],
                "开盘价_最大值": 开盘价_最大值,
                "开盘价_最小值": 开盘价_最小值,
                "收盘价_最大值": 收盘价_最大值,
                "收盘价_最小值": 收盘价_最小值,
                "最高价_最大值": 最高价_最大值,
                "最高价_最小值": 最高价_最小值,
                "最低价_最大值": 最低价_最大值,
                "最低价_最小值": 最低价_最小值
                }
    except:
        # print(traceback.format_exc())
        return {"DIF": "-", "DEA": "-", "MA30": "-", "MACD_today": "-", "MACD_yesterday": "-", 
                "MA5": "-", "MA10": "-", "MA20": "-", "MA30": "-", "MA60": "-", "MA100": "-",
                "MA3": "-", "MA7": "-", "MA12": "-",
                "EMA5": "-", "EMA13": "-", "EMA30": "-", "EMA60": "-",
                "ma5_yesterday": "-",
                "ma10_yesterday": "-",
                "ma20_yesterday": "-",

                "ma3_yesterday": "-",
                "ma7_yesterday": "-",
                "ma12_yesterday": "-",

                "EMA18": "-",
                "EMA13_上穿_EMA18": "-",

                "ma5_before": "-",
                "ma10_before": "-",
                "开盘价_最大值": "-",
                "开盘价_最小值": "-",
                "收盘价_最大值": "-",
                "收盘价_最小值": "-",
                "最高价_最大值": "-",
                "最高价_最小值": "-",
                "最低价_最大值": "-",
                "最低价_最小值": "-"
                }


def str2num(num):
    try:
        return float(num)
    except:
        return 0


def get_last_macd(scode, start_date=""):  # 获取最近日线
    try:
        if "." not in scode:
            scode_str = "1." + scode if scode[0] == "6" else "0." + scode
        else:
            scode_str = scode
        url = f"http://15.push2his.eastmoney.com/api/qt/stock/kline/get?&secid={scode_str}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&end=20500101&lmt=100000"

        r = Requests(url)
        js = r.json()
        sname = js["data"]["name"]
        df = pd.DataFrame(
            columns=["日期", "Open", "Close", "High", "Low"])  # 51日期，52开，53收，54高，55低，56交易量，57交易额，58振幅，59涨跌幅，60涨跌额，61换手率
        temp_dict = {"日期": [], "Open": [], "Close": [], "High": [], "Low": []}  # ,"Volume":[],"Amount":[]
        volume_list = []
        now = time.strftime("%Y-%m-%d", time.localtime())
        # if now >= ""
        # 股票名称，股票代码，开盘价，最高价，最低价，收盘价，成交量，成交额，涨跌幅，
        # MA5，MA10，MA30，MA60，MACD_today，MACD_yesterday，
        # 开盘价_最大值,开盘价_最小值,最高价_最大值,最高价_最小值,最低价_最大值,最低价_最小值,收盘价_最大值,收盘价_最小值

        for item in js["data"]["klines"][:-1]:  # 丢掉最后一行数据
            f51, f52, f53, f54, f55, f56, f57, f58, f59, f60, f61 = item.split(",")
            f52, f53, f54, f55, f56, f57 = [str2num(f52), str2num(f53), str2num(f54), str2num(f55), str2num(f56),
                                            str2num(f57)]
            # df.loc[f51] = [f52,f53,f54,f55,f56,f57]
            temp_dict["日期"].append(f51)
            temp_dict["Open"].append(f52)
            temp_dict["Close"].append(f53)
            temp_dict["High"].append(f54)
            temp_dict["Low"].append(f55)
            volume_list.append(f56)

        close_list = list(temp_dict["Close"]) + [str2num(js["data"]["klines"][-1].split(",")[2])]

        df = pd.DataFrame(temp_dict)

        if start_date != "":
            new_df = df[df["日期"] >= start_date]
            Open_max = new_df["Open"].max()
            Open_min = new_df["Open"].min()
            Close_max = new_df["Close"].max()
            Close_min = new_df["Close"].min()
            High_max = new_df["High"].max()
            High_min = new_df["High"].min()
            Low_max = new_df["Low"].max()
            Low_min = new_df["Low"].min()
        else:
            Open_max = "-"
            Open_min = "-"
            Close_max = "-"
            Close_min = "-"
            High_max = "-"
            High_min = "-"
            Low_max = "-"
            Low_min = "-"

        df["ema12"] = df["Close"].ewm(span=12, min_periods=1).mean()
        df["ema26"] = df["Close"].ewm(span=26, min_periods=1).mean()
        df["ema5"] = df["Close"].ewm(span=5, min_periods=1).mean()
        df["ema13"] = df["Close"].ewm(span=13, min_periods=1).mean()
        df["ema18"] = df["Close"].ewm(span=18, min_periods=1).mean()
        df["ema30"] = df["Close"].ewm(span=30, min_periods=1).mean()
        df["ema60"] = df["Close"].ewm(span=60, min_periods=1).mean()
        df["DIF"] = df["ema12"] - df["ema26"]
        df["DEA"] = df["DIF"].ewm(span=9, min_periods=1).mean()
        df["MACD"] = round((df["DIF"] - df["DEA"]) * 2, 4)

        sum4 = list(df["Close"][-4:])
        sum2 = list(df["Close"][-2:])
        sum6 = list(df["Close"][-6:])
        sum11 = list(df["Close"][-11:])

        sum9 = list(df["Close"][-9:])
        sum19 = list(df["Close"][-19:])
        sum29 = list(df["Close"][-29:])
        sum59 = list(df["Close"][-59:])
        sum99 = list(df["Close"][-99:])

        # 确保数据按日期升序排列
        df = df.sort_values(by="日期")

        # 计算昨日MA值 (使用到昨日为止的数据，包含昨日)
        df_yesterday = df  # 包含所有数据直到昨日
        
        # 计算昨日MA值
        sum5_yesterday = list(df_yesterday["Close"][-5:])
        sum10_yesterday = list(df_yesterday["Close"][-10:])
        sum20_yesterday = list(df_yesterday["Close"][-20:])
        
        sum3_yesterday = list(df_yesterday["Close"][-3:])
        sum7_yesterday = list(df_yesterday["Close"][-7:])
        sum12_yesterday = list(df_yesterday["Close"][-12:])

        # 计算前日MA值 (使用到前日为止的数据，包含前日)
        df_before = df.iloc[:-1]  # 不包含最后一天的数据
        sum5_before = list(df_before["Close"][-5:])
        sum10_before = list(df_before["Close"][-10:])
        
        sum3_before = list(df_before["Close"][-3:])
        sum7_before = list(df_before["Close"][-7:])
        sum12_before = list(df_before["Close"][-12:])

        # 计算昨日MA值
        ma5_yesterday = round(sum(sum5_yesterday) / len(sum5_yesterday), 3) if sum5_yesterday else "-"
        ma10_yesterday = round(sum(sum10_yesterday) / len(sum10_yesterday), 3) if sum10_yesterday else "-"
        ma20_yesterday = round(sum(sum20_yesterday) / len(sum20_yesterday), 3) if sum20_yesterday else "-"
        
        ma3_yesterday = round(sum(sum3_yesterday) / len(sum3_yesterday), 3) if sum3_yesterday else "-"
        ma7_yesterday = round(sum(sum7_yesterday) / len(sum7_yesterday), 3) if sum7_yesterday else "-"
        ma12_yesterday = round(sum(sum12_yesterday) / len(sum12_yesterday), 3) if sum12_yesterday else "-"

        # 计算前日MA值
        ma5_before = round(sum(sum5_before) / len(sum5_before), 3) if sum5_before else "-"
        ma10_before = round(sum(sum10_before) / len(sum10_before), 3) if sum10_before else "-"
        
        ma3_before = round(sum(sum3_before) / len(sum3_before), 3) if sum3_before else "-"
        ma7_before = round(sum(sum7_before) / len(sum7_before), 3) if sum7_before else "-"
        ma12_before = round(sum(sum12_before) / len(sum12_before), 3) if sum12_before else "-"

        return scode, {"dea": df["DEA"].iloc[-1],
                       "MACD_yesterday": df["MACD"].iloc[-1],
                       "ma5_yesterday": ma5_yesterday,
                       "ma10_yesterday": ma10_yesterday,
                       "ma20_yesterday": ma20_yesterday,
                       "ma5_before": ma5_before,
                       "ma10_before": ma10_before,
                       "ma3_yesterday": ma3_yesterday,
                       "ma7_yesterday": ma7_yesterday,
                       "ma12_yesterday": ma12_yesterday,
                       "ma3_before": ma3_before,
                       "ma7_before": ma7_before,
                       "ma12_before": ma12_before,
                       "ema12": df["ema12"].iloc[-1],
                       "ema26": df["ema26"].iloc[-1],
                       "ema5": df["ema5"].iloc[-1],
                       "ema13": df["ema13"].iloc[-1],
                       "ema18": df["ema18"].iloc[-1],
                       "ema30": df["ema30"].iloc[-1],
                       "ema60": df["ema60"].iloc[-1],
                       "sum4": sum4, "sum19": sum19, "sum9": sum9, "sum29": sum29, "sum59": sum59, "sum99": sum99,
                       "sum2": sum2, "sum6": sum6, "sum11": sum11,
                       "OCHL": [(Open_max, Open_min), (Close_max, Close_min), (High_max, High_min), (Low_max, Low_min)]
                       }
    except:
        # print(traceback.format_exc())
        return scode, {"dea": "-",
                       "MACD_yesterday": "-",
                       "ma5_yesterday": "-",
                       "ma10_yesterday": "-",
                       "ma20_yesterday": "-",
                       "ma5_before": "-",
                       "ma10_before": "-",
                       "ma3_yesterday": "-",
                       "ma7_yesterday": "-",
                       "ma12_yesterday": "-",
                       "ma3_before": "-",
                       "ma7_before": "-",
                       "ma12_before": "-",
                       "ema12": "-",
                       "ema26": "-",
                       "ema5": "-",
                       "ema13": "-",
                       "ema18": "-",
                       "ema30": "-",
                       "ema60": "-",
                       "sum4": [], "sum19": [], "sum9": [], "sum29": [], "sum59": [], "sum99": [],
                       "sum2": [], "sum6": [], "sum11": [],
                       "OCHL": []}


def handle_result(arg):
    global all_scode_last_dict
    scode, scode_dict = arg
    # print(f"历史数据始化完成{len(all_scode_last_dict)}：{scode}        \r", end="")
    all_scode_last_dict[scode] = scode_dict


def load_cached_data(kline_file):
    """从缓存文件中加载数据"""
    if kline_file.exists():
        with open(kline_file, "rb") as f:
            return pickle.load(f)
    return None


def get_last_data(scode_list, kline_file, start_date):
    global all_scode_last_dict
    all_scode_last_dict = {}
    p = pool.Pool()
    for scode in scode_list:
        p.apply_async(get_last_macd, args=(scode, start_date), callback=handle_result)
    p.close()
    p.join()

    print(f"日线历史数据缓存完成！")
    with open(kline_file, "wb") as f:
        pickle.dump(all_scode_last_dict, f)
    return all_scode_last_dict


def get_hs_stock_list():
    url = "https://12.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=10000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f2,f5,f3,f17,f16,f5,f15,f6,f10,f8,f14,f12,f20"
    r = Requests(url)
    result_list = []
    for item in r.json()["data"]["diff"]:
        scode = item["f12"]
        result_list.append(scode)
    return result_list


def get_hs_data(last_day_dict: dict, scode_list: list):
    url = "https://12.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=10000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f2,f5,f3,f17,f16,f5,f15,f6,f10,f8,f14,f12,f20"
    r = Requests(url)
    result_list = []
    for item in r.json()["data"]["diff"]:
        scode = item["f12"]
        if scode not in scode_list:
            continue
        try:
            dif_dict = get_macd_ma(Close=item["f2"], Open=item["f17"],
                                   High=item["f15"], Low=item["f16"],
                                   last_dict=last_day_dict[scode]
                                   )
            if item["f12"][0] in ["0", "3"]:
                market = "深市"
            elif item["f12"][0] in ["6"]:
                market = "沪市"
            else:
                market = "深市"

            row_dict = {
                "股票名称": item["f14"],
                "股票代码": item["f12"],
                "最新价": item["f2"],
                "涨幅": item["f3"],
                "市场": market,
                "开盘价": item["f17"],
                "最高价": item["f15"],
                "最低价": item["f16"],
                "成交量": item["f5"],
                "成交额": item["f6"]
            }
            row_dict.update(dif_dict)
            result_list.append(row_dict)
        except:
            # print(traceback.format_exc())
            continue
    url = f"https://push2.eastmoney.com/api/qt/ulist.np/get?fields=f2,f5,f3,f17,f16,f5,f15,f6,f10,f8,f14,f12,f20&invt=2&ut=bd1d9ddb04089700cf9c27f6f7426281&secids=1.000001"
    r = Requests(url)
    for item in r.json()["data"]["diff"]:
        scode = "1." + item["f12"]
        if scode not in scode_list:
            continue
        try:
            dif_dict = get_macd_ma(Close=item["f2"] / 100, Open=item["f17"] / 100,
                                   High=item["f15"] / 100, Low=item["f16"] / 100,
                                   last_dict=last_day_dict[scode]
                                   )
            if item["f12"][0] in ["0", "3"]:
                market = "深市"
            elif item["f12"][0] in ["6"]:
                market = "沪市"
            else:
                market = "深市"
            row_dict = {
                "股票名称": item["f14"],
                "股票代码": scode,
                "市场": market,
                "最新价": item["f2"] / 100,
                "涨幅": item["f3"] / 100,
                "开盘价": item["f17"] / 100,
                "最高价": item["f15"] / 100,
                "最低价": item["f16"] / 100,
                "成交量": item["f5"],
                "成交额": item["f6"]
            }
            row_dict.update(dif_dict)
            result_list.insert(0, row_dict)
        except:
            # print(traceback.format_exc())
            continue
    return result_list


def get_current_trade_day():
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.000001&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5&fields2=f51&klt=101&fqt=0&beg=20210501&end=20500101"
    r = Requests(url)
    return r.json()["data"]["klines"]


if __name__ == "__main__":
    """
    缓存历史日线数据，淘宝写的，用这个来计算历史的数据，存至data / 文件夹
    """
    trade_day_list = get_current_trade_day()
    yesterday, today = trade_day_list[-2:]
    print(f"- 时间校验，昨天日期为: {yesterday}, 今天日期为: {today}；当前时刻: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")

    import os
    if not os.path.exists("data"):
        os.mkdir("data")

    from datetime import datetime
    from_date = datetime(2022, 10, 1)

    # 定义股票号码
    scode_list = ["1.000001", "301338", "300554"]

    # 缓存机制
    id_str = "".join(scode_list) + from_date.strftime('%Y-%m-%d') + today
    from pathlib import Path
    import hashlib
    kline_file = Path(f"data/{hashlib.md5(id_str.encode()).hexdigest().upper()}.pkl")
    last_dict = get_last_data(scode_list, kline_file, from_date.strftime('%Y-%m-%d'))

    """
    通用Tick数据刷新接口
    """
    # 更新时刻
    start_time = time.time()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 更新最新Tick数据
    data_list = []
    data_list = get_hs_data(last_dict, scode_list)
    if len(data_list) != 0:
        for item in data_list:
            if item["股票代码"] == "1.000001":
                print(item)
            else:
                index = scode_list.index(item["股票代码"]) - 1
                print(index, item)

