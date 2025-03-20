# -*- coding: utf-8 -*-
# @Time : 2023/03/20
# @Author : 吴宇
# @File :
# @desc :

# ---------------------------- project 配置 ----------------------------

PROJECT_NAME = "common-yida-data-to-tidb"
# 补全项目名称(一定要写)
PROJECT_TITLE = "宜搭数据同步到tidb"
# 接口路由
prefix = f"/api/v1/{PROJECT_NAME}/schedule"


dingding_access_token_name = "common-dingding-access-token:common:access_token"

bus_category = {
    "LCS厨师项目部": "厨师鞋",
    "事业五部": "安全鞋",
    "LCN国内项目部": "安全鞋",
    "LS2安全鞋项目二部": "安全鞋",
    "LPF多元渠道项目部": "安全鞋",
    "FP流翎事业部": "休闲鞋",
    "事业一部": "安全鞋"
}