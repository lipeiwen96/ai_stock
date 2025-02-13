import calendar
import datetime
import tushare as ts
import chinese_calendar
import pandas as pd
from pandas import Series
from dateutil.relativedelta import relativedelta
import config


def str2date(s_date, format="%Y%m%d"):
    return datetime.datetime.strptime(s_date, format)


def str2pandasdate(s_date, format="%Y%m%d"):
    return pd.Timestamp(datetime.datetime.strptime(s_date, format))


def get_monthly_duration(start_date, end_date):
    """
    把开始日期到结束日期，分割成每月的信息
    比如20210301~20220515 =>
    [   [20210301,20210331],
        [20210401,20210430],
        ...,
        [20220401,20220430],
        [20220501,20220515]
    ]
    """
    start_date = str2date(start_date)
    end_date = str2date(end_date)
    years = list(range(start_date.year, end_date.year + 1))
    scopes = []
    for year in years:
        if start_date.year == year:
            start_month = start_date.month
        else:
            start_month = 1

        if end_date.year == year:
            end_month = end_date.month + 1
        else:
            end_month = 12 + 1

        for month in range(start_month, end_month):
            if start_date.year == year and start_date.month == month:
                s_start_date = date2str(datetime.date(year=year, month=month, day=start_date.day))
            else:
                s_start_date = date2str(datetime.date(year=year, month=month, day=1))
            if end_date.year == year and end_date.month == month:
                s_end_date = date2str(datetime.date(year=year, month=month, day=end_date.day))
            else:
                _, last_day = calendar.monthrange(year, month)
                s_end_date = date2str(datetime.date(year=year, month=month, day=last_day))
            scopes.append([s_start_date, s_end_date])

    return scopes


def get_yearly_duration(start_date, end_date):
    """
    把开始日期到结束日期，分割成每年的信息
    比如20210301~20220501 => [[20210301,20211231],[20220101,20220501]]
    """
    start_date = str2date(start_date)
    end_date = str2date(end_date)
    years = list(range(start_date.year, end_date.year + 1))
    scopes = [[f'{year}0101', f'{year}1231'] for year in years]

    if start_date.year == years[0]:
        scopes[0][0] = date2str(start_date)
    if end_date.year == years[-1]:
        scopes[-1][1] = date2str(end_date)
    return scopes


def duration(start, end, unit='day'):
    d0 = str2date(start)
    d1 = str2date(end)
    delta = d1 - d0
    if unit == 'day': return delta.days
    return None


def tomorrow(s_date=None):
    if s_date is None: s_date = today()
    return future('day', 1, s_date)


def yesterday(s_date=None):
    if s_date is None: s_date = today()
    return last_day(s_date, 1)


def last(date_type, unit, s_date):
    return __date_span(date_type, unit, -1, s_date)


def last_year(s_date, num=1):
    return last('year', num, s_date)


def last_month(s_date, num=1):
    return last('month', num, s_date)


def last_week(s_date, num=1):
    return last('week', num, s_date)


def last_day(s_date, num=1):
    return last('day', num, s_date)


def today():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%Y%m%d")


def now():
    return datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S")


def nowtime():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%H:%M:%S")


def future(date_type, unit, s_date):
    return __date_span(date_type, unit, 1, s_date)


def __date_span(date_type, unit, direction, s_date):
    """
    last('year',1,'2020.1.3')=> '2019.1.3'
    :param unit:
    :param date_type: year|month|day
    :return:
    """
    the_date = str2date(s_date)
    if date_type == 'year':
        return date2str(the_date + relativedelta(years=unit) * direction)
    elif date_type == 'month':
        return date2str(the_date + relativedelta(months=unit) * direction)
    elif date_type == 'week':
        return date2str(the_date + relativedelta(weeks=unit) * direction)
    elif date_type == 'day':
        return date2str(the_date + relativedelta(days=unit) * direction)
    else:
        raise ValueError(f"无法识别的date_type:{date_type}")


def date2str(date, format="%Y%m%d"):
    return datetime.datetime.strftime(date, format)


def dataframe2series(df):
    if type(df) == Series: return df
    assert len(df.columns) == 1, df.columns
    return df.iloc[:, 0]


def get_last_trade_date_of_month(df):
    """
    得到每个月的最后一天的交易日
    :param df_trade_date: 所有交易日
    :return: 只保留每个月的最后一个交易日，其他剔除掉
    """
    df[df.index.day == df.index.days_in_month]


def get_last_trade_date(end_date, trade_dates, include_today=False):
    """
    得到日期范围内的最后的交易日，end_date可能不在交易日里，所以要找一个最近的日子
    :param df_trade_date: 所有交易日
    :return: 只保留每个月的最后一个交易日，其他剔除掉
    """
    # 反向排序
    trade_dates = trade_dates.tolist()
    trade_dates.reverse()

    # 寻找合适的交易日期
    for trade_date in trade_dates:

        if include_today:
            # 从最后一天开始找，如果交易日期(trade_date)比目标日期(end_date)小了，就找到了
            if trade_date <= end_date:
                return trade_date
        else:
            if trade_date < end_date:
                return trade_date

    return None


def get_holidays(from_year: int = 2012, include_weekends: bool = False):
    """
    获取所有节假日，默认从2004年开始,chinese_calendar只支持到2004
    """
    to_year = datetime.datetime.now().year
    start = datetime.date(from_year, 1, 1)
    end = datetime.date(to_year, 12, 31)
    holidays = chinese_calendar.get_holidays(start, end, include_weekends)
    return holidays


def tushare_api():
    ts.set_token(config.PURCHASED_GENERAL_TOKEN)
    return ts.pro_api()


def is_trade_day():
    """
    判断是不是交易时间：9：30~11:30
    :return:
    """
    trade_dates = list(tushare_api().trade_cal(start_date=last_week(today()), end_date=today()))
    if today() in trade_dates:
        return True
    return False


def last_trade_day(last_num: int = -1):
    df = all_trade_data(start_date="20230101", end_date=today())
    return df.iloc[last_num].strftime('%Y%m%d')


def all_trade_data(start_date="20220101", end_date="20231022"):
    df = tushare_api().trade_cal(start_date=start_date, end_date=end_date, is_open="1")
    df = df.sort_values(by='cal_date', ascending=True)
    df = df.reset_index(drop=True)
    data_range = pd.to_datetime(df['cal_date'], format='%Y%m%d')
    return data_range


def is_monitoring_time(all_time_monitoring: bool = False):
    """
    是否在监控时间范围
    """
    if all_time_monitoring:
        return True
    else:
        FMT = '%H:%M:%S'
        now_time = datetime.datetime.strftime(datetime.datetime.now(), FMT)
        start_time = "04:00:00"
        end_time = "15:00:00"
        return start_time <= now_time <= end_time


def is_trade_time(all_time_trading: bool = False):
    if all_time_trading:
        return True
    else:
        FMT = '%H:%M:%S'
        now_time = datetime.datetime.strftime(datetime.datetime.now(), FMT)
        # print(now_time)
        time_0930 = "09:30:00"
        time_1130 = "11:30:00"
        time_1300 = "13:00:00"
        time_1500 = "15:00:00"
        is_morning = time_0930 <= now_time <= time_1130
        is_afternoon = time_1300 <= now_time <= time_1500
        return is_morning or is_afternoon


if __name__ == "__main__":
    print(f"当前时刻：{now()}，是否为交易日：{is_trade_day()}，是否为交易时间：{is_trade_time()}")
    print(f"今年所有的节假日：{get_holidays(from_year=2023, include_weekends=False)}")
    print(f"now: {now()}, nowtime: {nowtime()}, yesterday: {yesterday()}, today: {today()}, tomorrow: {tomorrow()}")
    print(f"{get_yearly_duration(start_date='20221030', end_date='20231029')}")
    print(last_trade_day())