
import os

def get_static_tp_ratio():
    return STATIC_TP_RATIO

def set_static_tp_ratio(value):
    global STATIC_TP_RATIO
    STATIC_TP_RATIO = value

# data downloader config
# TUSHARE-SDK Token
My_TOKEN = os.getenv("MY_TOKEN", "b78d230c7ab25ba6ba198c33cfdf29a5a23868321746cc76dcdd4830")
# 通用token
PURCHASED_GENERAL_TOKEN = os.getenv("PURCHASED_GENERAL_TOKEN", 'f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')
# 分钟级token
PURCHASED_MIN_TOKEN = os.getenv("PURCHASED_MIN_TOKEN", "f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108")

# 分钟级行情包含选项
MIN_FREQ_SET = ["1min", "5min", "10min", "15min", "30min", "60min"]

# 每日包含的分钟数据量
DAILY_TOTAL_MIN_VALUE = 241
# Tushare接口分钟级API的上限访问值为8000，为了保险设置为7500
TUSHARE_API_LIMIT_VALUE = 7500

ACCOUNT_BASE_URL = 'http://127.0.0.1:9999'
# ACCOUNT_BASE_URL = 'http://192.168.18.21:9999'

CANNOT_USE_CASH_RATE = 0
MAX_POSITION_RATE = 0.15
STATIC_SL_RATIO = 0.15
STATIC_TP_RATIO = 0.25
DYNAMIC_TP_RATIO = 0.66
MIN_BUY_PRICE = 100

ORIGINAL_CASH = 50000
MIN_VALUE = 10000
EXPECT_VALUE = 15000
MAX_VALUE = 30000  # 20231119加入单股上限买入量
# 税率
COMMISSION_RATE = 0.0005
