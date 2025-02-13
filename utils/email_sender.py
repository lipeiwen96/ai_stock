"""
邮件发送组件
"""
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from modules.stock import Stock


# 设置你的邮箱信息
MAIL_HOST = 'smtp.163.com'
MAIL_USER = 'lpwseu@163.com'
MAIL_PWD = 'XGQFKHWNRHGOCJHU'
reminder = [
    {
        "recipient_email": "472650539@qq.com",
        "name": "LPW",
        "is_host": True,
    },
    # {
    #     "recipient_email": "17612188@qq.com",
    #     "name": "GH",
    #     "is_host": True,
    # },
]


def auto_send_email(head: str, message: str, mode: str = "all", start: bool = False):
    if start:
        print("【启动邮件通知服务】")
        only_host = False if mode == "all" else True

        print(f"- {'主机模式' if only_host else '群发模式'}")
        print(f"- 标题: {head}")
        # print(f"- 主体: {message}")

        for row in reminder:
            if only_host:
                if row["is_host"]:
                    pass
                else:
                    continue

            recipient_email = row['recipient_email']
            name = row['name']

            # create email message
            msg = MIMEMultipart()
            msg['From'] = MAIL_USER
            msg['To'] = recipient_email
            msg['Subject'] = head
            msg.attach(MIMEText(message, 'html'))

            try:
                s = smtplib.SMTP_SSL(MAIL_HOST, 465)
                s.login(MAIL_USER, MAIL_PWD)
                s.sendmail(MAIL_USER, recipient_email, msg.as_string())
                s.close()
                print(f"- [邮件成功提示]已向用户 {name} 的邮箱: {recipient_email} 进行通知")
            except Exception as e:
                print(f"- [邮件失败提示]向用户 {name} 的邮箱: {recipient_email} 通知失败，错误为{e}")

        print("【退出邮件通知服务】\n")


def error_message_sender(error_message: str, mode: str = "host", start: bool = True):
    message = f"""
            <p>出现意外错误: </p>
            <br>
            <strong>{error_message}</strong> </p>
            <br>

            <p style="color: #999999;"> 请远程连接主机重启爬虫 <br>
            <p style="color: #999999;"> 向日葵识别码: <strong>129538920</strong> <br>
            <p style="color: #999999;"> 长期验证码: <strong>lpw0821</strong> <br>
            <p style="color: #999999;"> 向日葵下载地址: http://url.oray.com/tGJdas/ <br>
            """
    auto_send_email(head=f"【OldSockTool-V1.0 Warning】Data Source Exception, Please Reconnect！",
                    message=message, mode=mode, start=start)


def start_message_sender(account, mode: str = "host", start: bool = True):
    message = f"""
                <p>Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}</p>
                <br>
                <p><strong>当前持仓信息</strong> </p>
                <br>
                <p>{account.log}</p>
                <br>

                <p style="color: #999999;"> 请远程连接主机重启爬虫 <br>
                <p style="color: #999999;"> 向日葵识别码: <strong>129538920</strong> <br>
                <p style="color: #999999;"> 长期验证码: <strong>lpw0821</strong> <br>
                <p style="color: #999999;"> 向日葵下载地址: http://url.oray.com/tGJdas/ <br>
                """
    auto_send_email(head=f"【OldSockTool-V1.0 Starting】Wishing You Success！",
                    message=message, mode=mode,
                    start=start)


def buy_message_sender(stock: Stock, now: str, start: bool):
    message = f"""
                  <p> <strong> {stock.log_name} </strong> {now}时刻 第{stock.buy_trigger.trigger_times}次买入预警提示：触发买入交易条件 </p>
                  <br>
                  <p> {stock.tick.log} </p>
                  <br>
                  <p> {stock.log_buy_strategy} </p>
                  <br>
                  <br>
                  <p style="color: #999999;"> 请远程连接主机重启爬虫 <br>
                  <p style="color: #999999;"> 向日葵识别码: <strong>129538920</strong> <br>
                  <p style="color: #999999;"> 长期验证码: <strong>lpw0821</strong> <br>
                  <p style="color: #999999;"> 向日葵下载地址: http://url.oray.com/tGJdas/ <br>
                """
    head = f"【OldSockTool - BUY TRIGGER】 {stock.log_name} - {stock.buy_trigger.expect_price}元 " \
           f"({stock.buy_trigger.expect_min_price} ~ {stock.buy_trigger.expect_max_price})元!"
    auto_send_email(
        head=head,
        message=message, mode="all", start=start)


def sell_message_sender(stock: Stock, now: str, start: bool):
    message = f"""
                  <p> <strong> {stock.log_name} </strong> {now}时刻 第{stock.sell_trigger.trigger_times}次卖出预警提示：触发卖出交易条件 </p>
                  <br>
                  <p> {stock.log_position} </p>
                  <br>
                  <p> {stock.tick.log} </p>
                  <br>
                  <p> {stock.log_sell_strategy} </p>
                  <br>
                  <br>
                  <p style="color: #999999;"> 请远程连接主机重启爬虫 <br>
                  <p style="color: #999999;"> 向日葵识别码: <strong>129538920</strong> <br>
                  <p style="color: #999999;"> 长期验证码: <strong>lpw0821</strong> <br>
                  <p style="color: #999999;"> 向日葵下载地址: http://url.oray.com/tGJdas/ <br>
                """
    head = f"【SockTool - SELL TRIGGER】 {stock.log_name} - {stock.sell_trigger.expect_price}元 " \
           f"({stock.sell_trigger.expect_min_price} ~ {stock.sell_trigger.expect_max_price})元!"
    auto_send_email(
        head=head,
        message=message, mode="all", start=start)


def end_message_sender(account, mode: str = "host", start: bool = True):
    message = f"""
                <p>End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 交易时间结束; 已退出 | 轻量化Stock自动交易工具V1.0 | 数据端 </p>
                <br>
                <p><strong>当前持仓信息</strong> </p>
                <br>
                <p>{account.log}</p>
                <br>

                <p style="color: #999999;"> 请远程连接主机重启爬虫 <br>
                <p style="color: #999999;"> 向日葵识别码: <strong>129538920</strong> <br>
                <p style="color: #999999;"> 长期验证码: <strong>lpw0821</strong> <br>
                <p style="color: #999999;"> 向日葵下载地址: http://url.oray.com/tGJdas/ <br>
                """
    auto_send_email(head=f"【OldSockTool-V1.0 Ending】See You Tomorrow！",
                    message=message, mode=mode,
                    start=start)