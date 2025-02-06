# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:


# ---------------------------- project 配置 ----------------------------
PROJECT_NAME = "crawler-temu-seller-kuajingmaihuo-data"

# 补全项目名称(一定要写)
PROJECT_TITLE = "temu数据自动采集"
# 接口路由
PROJECT_ROUTE = f"/api/v1/{PROJECT_NAME}/schedule"

operatorId = '6TAkDDIe6iiS2cXJBVGMWzAiEiE'  # yarm

dingding_api = 'https://oapi.dingtalk.com/robot/send?access_token=3f296e744bfdfd5f2694078a9d4e9b6793576c4fc441793b760be744335fd343'

illegalidata = {
    'violationType': {
        '1': '延迟到货',
        '2': '虚假交易',
        '3': '异常轨迹',
        '4': '虚假发货',
        '5': '缺货',
        '6': '欺诈发货',
        '8': '加收运费违规',
    },
    'exceptionTypeList': {
        '1': '轨迹节点时间过早',
        '2': '异地签收',
        '5': '物流单号异常',
        '0': '其他',
    },
    'appealProgress': {
        '0': '待申述',
        '1': '待完善资料',
        '2': '平台处理中',
        '3': '处理完成',
        '4': '超时关闭申述',
    },
}

# mongo数据库名
db_name = 'ods_crawler_temu'
# 商品列表
mg_product_list_field_list = ['productSkcId', 'productId']
table_name = 'ods_crawler_temu_seller_product_list_i_d'
# 长期活动
mg_salesactlong_field_list = ['productId', 'skcId', 'goodsId', 'enrollTime', 'mallId']
salesactlong_table_name = 'ods_crawler_temu_seller_salesactlong_list_i_d'
# 专题活动
mg_thematicact_field_list = ['productId', 'skcId', 'id', 'signUpTime', 'mallId']
thematicact_table_name = 'ods_crawler_temu_seller_salesthematicact_list_i_d'
# temu-跨境卖家中心-订单管理-订单列表-买家履约订单
mg_orderlist_field_list = ['parentOrderSn', 'mallId']
orderlist_table_name = 'ods_crawler_temu_seller_order_list_i_d'
