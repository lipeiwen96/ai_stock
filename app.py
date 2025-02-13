import streamlit as st
import sys
import os
from stock_sentinel.stock_selector import StockSelector
from datetime import datetime
import pandas as pd

# 添加模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置页面标题和布局
st.set_page_config(
    page_title="智能选股器 V0.1",
    layout="wide"
)


def main():
    # 设置页面样式
    st.markdown("""
        <style>
        .group-box {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 8px;
            margin-bottom: 20px;
            margin-right: 50px;
            background-color: #f9f9f9;
        }
        .group-title {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .intro-card {
            background-color: #f5f5f7;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 16px;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("智能选股器 V0.1")

    # 介绍卡片
    st.markdown("""
        <div class='intro-card'>
            <strong>版本内容：</strong> 本版本提供了智能选股功能，支持基础指标：EMA5、EMA13、EMA30、EMA60、MA100。
            <br><strong>作者：</strong> @搞量化的猪咪
        </div>
    """, unsafe_allow_html=True)
    # <br><strong>作者：</strong> @搞量化的猪咪

    # 参数设置
    st.sidebar.header("参数设置")

    # 前端增加一个日历输入选项，名称为股票发布日期起始限制（过滤输入日期后发布的股票），默认数值为2022-10-01
    from_date = st.sidebar.date_input(
        "股票发布日期起始限制（过滤输入日期后发布的股票）",
        value=datetime(2022, 10, 1).date()
    )
    # 将其转化为datetime格式 如 from_date = datetime(2022, 10, 1)
    from_date = datetime.combine(from_date, datetime.min.time())

    a_value = st.sidebar.slider(
        "设置EMA5的上限阎值参数 a (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
        help="用于计算 EMA5 的阎值：股价 < EMA5*(1+a%)"
    )

    b_value = st.sidebar.slider(
        "设置EMA13的上限阎值参数 b (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
        help="用于计算 EMA13 的阎值：股价 < EMA13*(1+b%)"
    )

    c_value = st.sidebar.slider(
        "设置EMA30的上限阎值参数 c (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
        help="用于计算 EMA30 的阎值：股价 < EMA30*(1+c%)"
    )

    d_value = st.sidebar.slider(
        "设置EMA60的上限阎值参数 d (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
        help="用于计算 EMA60 的阎值：股价 < EMA60*(1+d%)"
    )

    e_value = st.sidebar.slider(
        "设置MA100的上限阎值参数 e (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
        help="用于计算 MA100 的阎值：股价 < MA100*(1+e%)"
    )

    # 筛选条件设置
    st.subheader("🌏 筛选条件设置")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 股价条件")

        # EMA5 分组
        st.markdown("<div class='group-box'><strong>EMA5筛选股价</strong></div>", unsafe_allow_html=True)
        price_above_ema5 = st.checkbox("股价 > EMA5", value=False)
        price_below_ema5 = st.checkbox(f"股价 < EMA5*(1+ &nbsp;**:red[{a_value}%]** &nbsp;) &nbsp;ℹ️由参数a控制", value=False,
                                       help="此条件使用侧边栏中的参数a来控制价格偏离EMA5的最大百分比")
        st.markdown("</div>", unsafe_allow_html=True)

        # EMA13 分组
        st.markdown("<div class='group-box'><strong>EMA13筛选股价</strong></div>", unsafe_allow_html=True)
        price_above_ema13 = st.checkbox("股价 > EMA13", value=False)
        price_below_ema13 = st.checkbox(f"股价 < EMA13*(1+ &nbsp;**:red[{b_value}%]** &nbsp;) &nbsp;ℹ️由参数b控制",
                                        help="此条件使用侧边栏中的参数b来控制价格偏离EMA13的最大百分比")
        st.markdown("</div>", unsafe_allow_html=True)

        # EMA30 分组
        st.markdown("<div class='group-box'><strong>EMA30筛选股价</strong></div>", unsafe_allow_html=True)
        price_above_ema30 = st.checkbox("股价 > EMA30", value=False)
        price_below_ema30 = st.checkbox(f"股价 < EMA30*(1+ &nbsp;**:red[{c_value}%]** &nbsp;) &nbsp;ℹ️由参数c控制",
                                        help="此条件使用侧边栏中的参数c来控制价格偏离EMA30的最大百分比", value=False)
        st.markdown("</div>", unsafe_allow_html=True)

        # EMA60 分组
        st.markdown("<div class='group-box'><strong>EMA60筛选股价</strong></div>", unsafe_allow_html=True)
        price_above_ema60 = st.checkbox("股价 > EMA60", value=False)
        price_below_ema60 = st.checkbox(f"股价 < EMA60*(1+ &nbsp;**:red[{d_value}%]** &nbsp;) &nbsp;ℹ️由参数d控制",
                                        help="此条件使用侧边栏中的参数d来控制价格偏离EMA60的最大百分比")
        st.markdown("</div>", unsafe_allow_html=True)

        # MA100 分组
        st.markdown("<div class='group-box'><strong>MA100筛选股价</strong></div>", unsafe_allow_html=True)
        price_above_ma100 = st.checkbox("股价 > MA100", value=False)
        price_below_ma100 = st.checkbox(f"股价 < MA100*(1+ &nbsp;**:red[{e_value}%]** &nbsp;) &nbsp;ℹ️由参数e控制",
                                        help="此条件使用侧边栏中的参数e来控制价格偏离MA100的最大百分比")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 📈 技术指标")
        ema13_above_ema30 = st.checkbox("EMA13 > EMA30")
        ema13_above_ema60 = st.checkbox("EMA13 > EMA60", value=False)
        ema13_above_ma100 = st.checkbox("EMA13 > MA100", value=False)
        ema30_above_ema60 = st.checkbox("EMA30 > EMA60")
        ema60_above_ma100 = st.checkbox("EMA60 > MA100")
        ema13_cross_ema18 = st.checkbox("【新增指标】EMA13上穿EMA18", value=True)

    if st.button("开始选股"):
        # 初始化选股器
        selector = StockSelector()
        with st.spinner("正在初始化股票池..."):
            selector.init_stock_pool(from_date)
            selector.add_cache(from_date)
            selector.renew_tick()

        # 构建筛选条件列表
        conditions = [
            {"type": "PRICE_ABOVE_EMA5", "enabled": price_above_ema5},
            {"type": "PRICE_BELOW_EMA5", "enabled": price_below_ema5, "percentage": a_value / 100},
            {"type": "PRICE_ABOVE_EMA13", "enabled": price_above_ema13},
            {"type": "PRICE_BELOW_EMA13", "enabled": price_below_ema13, "percentage": b_value / 100},
            {"type": "PRICE_ABOVE_EMA30", "enabled": price_above_ema30},
            {"type": "PRICE_BELOW_EMA30", "enabled": price_below_ema30, "percentage": c_value / 100},
            {"type": "PRICE_ABOVE_EMA60", "enabled": price_above_ema60},
            {"type": "PRICE_BELOW_EMA60", "enabled": price_below_ema60, "percentage": d_value / 100},
            {"type": "PRICE_ABOVE_MA100", "enabled": price_above_ma100},
            {"type": "PRICE_BELOW_MA100", "enabled": price_below_ma100, "percentage": e_value / 100},
            {"type": "EMA13_ABOVE_EMA30", "enabled": ema13_above_ema30},
            {"type": "EMA13_ABOVE_EMA60", "enabled": ema13_above_ema60},
            {"type": "EMA13_ABOVE_MA100", "enabled": ema13_above_ma100},
            {"type": "EMA30_ABOVE_EMA60", "enabled": ema30_above_ema60},
            {"type": "EMA60_ABOVE_MA100", "enabled": ema60_above_ma100},
            {"type": "EMA13_CROSS_EMA18", "enabled": ema13_cross_ema18}
        ]

        # 执行筛选
        with st.spinner("正在筛选股票..."):
            print("网页端参数为")
            print(conditions)
            filtered_stocks = selector.filter_stocks(conditions)

            # 显示结果
            st.subheader(f"筛选结果 (共{len(filtered_stocks)}只股票)")
            if filtered_stocks:
                # 处理并导出股票数据
                excel_file_path = process_stock_raw_data(conditions, filtered_stocks)

                # 提供下载按钮
                with open(excel_file_path, "rb") as file:
                    st.download_button(
                        label="下载筛选结果",
                        data=file,
                        file_name=os.path.basename(excel_file_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.write("没有找到符合条件的股票")


def process_stock_raw_data(conditions, filtered_stocks):
    stock_data = []

    for stock in filtered_stocks:
        stock_info = {
            "股票ID": stock.stock_code,
            "股票名称": stock.stock_name,
            "股票市场": stock.tick.market,
            "股票当前价格": stock.tick.price
        }

        # Add EMA and MA values if corresponding conditions are enabled
        stock_info["EMA5"] = stock.tick.ema_5
        stock_info["EMA13"] = stock.tick.ema_13
        stock_info["EMA18"] = stock.tick.ema_18
        stock_info["EMA13_上穿_EMA18"] = stock.tick.ema_13_cross_ema_18
        stock_info["EMA30"] = stock.tick.ema_30
        stock_info["EMA60"] = stock.tick.ema_60
        stock_info["MA100"] = stock.tick.ma_100

        # if any(condition["type"] == "PRICE_ABOVE_EMA5" and condition["enabled"] for condition in conditions) or \
        #         any(condition["type"] == "PRICE_BELOW_EMA5" and condition["enabled"] for condition in conditions):
        #     stock_info["EMA5"] = stock.tick.ema_5
        # if any(condition["type"] == "PRICE_ABOVE_EMA13" and condition["enabled"] for condition in conditions) or \
        #         any(condition["type"] == "PRICE_BELOW_EMA13" and condition["enabled"] for condition in conditions) or \
        #             any(condition["type"] == "EMA13_ABOVE_EMA30" and condition["enabled"] for condition in conditions) or \
        #             any(condition["type"] == "EMA13_ABOVE_EMA60" and condition["enabled"] for condition in conditions) or \
        #             any(condition["type"] == "EMA13_ABOVE_MA100" and condition["enabled"] for condition in conditions):
        #     stock_info["EMA13"] = stock.tick.ema_13
        # if any(condition["type"] == "PRICE_ABOVE_EMA30" and condition["enabled"] for condition in conditions) or \
        #         any(condition["type"] == "PRICE_BELOW_EMA30" and condition["enabled"] for condition in conditions) or \
        #             any(condition["type"] == "EMA13_ABOVE_EMA30" and condition["enabled"] for condition in conditions) or \
        #             any(condition["type"] == "EMA30_ABOVE_EMA60" and condition["enabled"] for condition in conditions):
        #     stock_info["EMA30"] = stock.tick.ema_30
        # if any(condition["type"] == "PRICE_ABOVE_EMA60" and condition["enabled"] for condition in conditions) or \
        #         any(condition["type"] == "PRICE_BELOW_EMA60" and condition["enabled"] for condition in conditions) or \
        #             any(condition["type"] == "EMA13_ABOVE_EMA60" and condition["enabled"] for condition in conditions)or \
        #             any(condition["type"] == "EMA30_ABOVE_EMA60" and condition["enabled"] for condition in conditions)or \
        #             any(condition["type"] == "EMA60_ABOVE_MA100" and condition["enabled"] for condition in conditions):
        #     stock_info["EMA60"] = stock.tick.ema_60
        # if any(condition["type"] == "PRICE_ABOVE_MA100" and condition["enabled"] for condition in conditions) or \
        #         any(condition["type"] == "PRICE_BELOW_MA100" and condition["enabled"] for condition in conditions) or \
        #             any(condition["type"] == "EMA13_ABOVE_MA100" and condition["enabled"] for condition in conditions)or \
        #             any(condition["type"] == "EMA60_ABOVE_MA100" and condition["enabled"] for condition in conditions):
        #     stock_info["MA100"] = stock.tick.ma_100

        stock_info["详细信息"] = stock.log_tick
        stock_data.append(stock_info)

    df = pd.DataFrame(stock_data)
    st.dataframe(df)

    # 导出 Excel 文件，文件名带上当前日期小时分钟秒
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file_name = f"stocks_{current_time}.xlsx"
    excel_file_path = os.path.abspath(os.path.join("files", "sentinel_files", excel_file_name))
    df.to_excel(excel_file_path, index=False)
    return excel_file_path


if __name__ == "__main__":
    main()
