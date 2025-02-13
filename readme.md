# 数据端（主线程）
@ Peiwen Li

## 数据端框架

#### 定点启动（初始化）
* 加载预先设定的股票池
* 加载账户资金、持仓信息

#### 实时加载（动态）
* 调用东方财富接口等后台接口，获取实盘秒级数据
* 使用实盘数据调用策略端口，返回每只股票的策略状态
* 使用交易主脑，生成交易信号，给交易操作端口
* 监测端口返回状态（这里需要异步操作），对未成订单进行追加监控（看实在哪边实现）
* 每次操作的消息通知系统

#### 定点退出（结束进程）
* 返回每日操作后台报告，总结当日收益及历史总收益


## 开发进展
20231029进展：优化一版数据端+策略端

* TODO-1: 动态止盈暂时无法实现，需要解决建仓时间问题
* TODO-2: 买卖单只能创建，暂不支持挂单成交查询，撤单，补单
* TODO-3: 买卖单价格问题，如果价格偏差于现价过多，如何操作
* TODO-4: 模拟操作过于耗时，怎么设置异步及任务系统，使主线程仍然继续
* TODO-5: 检测到当日已下订单后，就不要再重复下单
* TODO-6: 日志系统，每日交易信息存储


比较严重的问题：
下单成果后同花顺会出现提示，导致交易端操作失效


