# -*- coding: utf-8 -*-
# @Time    : 2023/5/23 15:52
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    : 
# @Software: 配置文件
# ---------------------------- project 配置 ----------------------------


PROJECT_NAME = "crawler-lingxing-finance-data"
# 补全项目名称(一定要写)
PROJECT_TITLE = "领星财务数据采集服务(爬虫)"
# 接口路由
PROJECT_ROUTE = f"/api/v1/{PROJECT_NAME}/schedule"

report_order_url = "https://gw.lingxingerp.com/bd/profit/report/report/order/list"  # 利润报表订单页面url
report_shop_url = "https://gw.lingxingerp.com/bd/profit/report/report/seller/list"  # 利润报表店铺页面url
report_msku_url = 'https://gw.lingxingerp.com/bd/profit/report/report/msku/list'  # 利润报表数据
report_msku_cost_url = 'https://gw.lingxingerp.com/bd/profit/report/report/cost/details/get'  # 利润报表价格
fc_settlement_summary_api_url = 'https://gw.lingxingerp.com/bd/sp/api/settlement/summary/list'   #亚马逊结算汇总
report_order_transaction_url = 'https://gw.lingxingerp.com/bd/profit/report/report/transaction/list' #利润报表-订单transaction视图-url

# 利润报表-msku维度任务队列
report_msku_queue = 'crawler-lingxing-finance-data:task:crawler_lx_profit_statement_data'
report_msku_cost_queue = 'crawler-lingxing-finance-data:task:crawler_lx_profit_statement_cost_detail3'
