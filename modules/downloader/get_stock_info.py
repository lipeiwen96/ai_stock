"""
TUSHARE 获得股票名称、代号等信息
"""
import tushare as ts
import config
import random
import pandas as pd
random.seed(88)


def get_stock_code_list(hs_type: str = "SH"):
    # 初始化TOKEN信息
    ts.set_token(config.PURCHASED_MIN_TOKEN)  # 分钟级行情
    pro = ts.pro_api()
    if hs_type == "SH":
        print("启用【分钟级行情的TOKEN】,获取上海股票数据")
        df = pro.hs_const(hs_type='SH')
    elif hs_type == "SZ":
        print("启用【分钟级行情的TOKEN】,获取深圳股票数据")
        df = pro.hs_const(hs_type='SZ')

    return [df.loc[i, "ts_code"].split(".")[0] for i in range(len(df))]


def get_total_stock_code(input_code: str = ""):
    """
    自动判断交易所
    """
    if ".SZ" in input_code or ".SH" in input_code:
        return input_code
    else:
        if input_code[0] == '6':
            return input_code + ".SH"
        else:
            return input_code + ".SZ"


def get_stock_code_and_name_list(start_year: int = 2019):
    # 初始化TOKEN信息
    ts.set_token(config.PURCHASED_GENERAL_TOKEN)
    pro = ts.pro_api()
    print("启用【5000积分通用TOKEN】,获取全盘股票数据")
    df = pro.stock_basic(exchange='',
                         list_status='L',  # 上市状态 L上市 D退市 P暂停上市，默认是L
                         fields='ts_code,name,list_date')
    output = []
    for i in range(len(df)):
        data_y = int(df.loc[i, "list_date"][:4])
        if data_y <= start_year:
            output.append([df.loc[i, "ts_code"].split(".")[0], df.loc[i, "name"]])
        else:
            # TODO: 这里涉及到对股票的缺失值进行补全，anyway，先挂着
            pass
    return output


def get_trade_date_range(start_date: str = '20180101', end_date: str = '20181231'):
    # 初始化TOKEN信息
    ts.set_token(config.PURCHASED_GENERAL_TOKEN)
    pro = ts.pro_api()
    print("启用【5000积分通用TOKEN】,获取全盘股票数据")
    df = pro.trade_cal(start_date=start_date, end_date=end_date, is_open="1")
    df = df.sort_values(by='cal_date', ascending=True)
    df = df.reset_index(drop=True)
    data_range = pd.to_datetime(df['cal_date'], format='%Y%m%d')
    print(f"【交易日检测】检测到您交易时间范围中的全部交易日为:")
    print(data_range)
    return data_range


def get_random_stock_code_and_name_list(stock_num: int = 10):
    all_info = get_stock_code_and_name_list()
    return random.sample(all_info, stock_num)
