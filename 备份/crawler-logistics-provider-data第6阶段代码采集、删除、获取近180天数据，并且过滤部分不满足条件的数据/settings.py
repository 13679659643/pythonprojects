# -*- coding: utf-8 -*-
# @Time    : 2024/8/14 9:30
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software: 接口  token  网页 配置文件
from db_model import ods_scg_wld_logistics_trace_db_table, \
    ods_scg_wld_logistics_trace_table_i_d, \
    ods_scg_wld_logistics_trace_table_i_d_field_list, ods_scg_wld_logistics_trace_db_view, \
    ods_scg_wld_logistics_trace_view_i_d, ods_scg_wld_logistics_trace_view_i_d_field_list, \
    truncate_ods_scg_wld_logistics_trace_table_i_d, truncate_ods_scg_wld_logistics_trace_view_i_d, \
    ods_scg_wld_tw_logistics_trace_db_table, ods_scg_wld_tw_logistics_trace_table_i_d, \
    truncate_ods_scg_wld_tw_logistics_trace_table_i_d, ods_scg_wld_tw_logistics_trace_table_i_d_field_list, \
    ods_scg_wld_logistics_ahc_table

PROJECT_NAME = "crawler-logistics-provider-data"
# 补全项目名称(一定要写)
PROJECT_TITLE = "爬虫获取物流相关数据"
# 接口路由
PROJECT_ROUTE = f"/api/v1/{PROJECT_NAME}/schedule"

# # 数据服务告警通知
# webhook = "https://oapi.dingtalk.com/robot/send?access_token=8b5c9d608f68b168e8d86b49a1efcb888703dc1a9ca24c754c2810fd00d7e95b"
#
# # 子服务
# fba_shipment_details_subserver = "crawler_customer_review_data"  # 爬取评论客服
#
# # 领星客服评论数据
# URL_REVIEW_API = 'https://erp.lingxing.com/api/customer_service/showReview'
#
# # MongoDB
# mongo_field_list = ['review_id']
# db_name, table_name = "ods_crawler_lingxing", "ods_lingxing_customer_review_d"


fetcher_info = {
    'GES': {
        "logistics_provider": "东方环球物流",
        "hash_token_path": "crawler-deliverr-logistics:common",
        "token_key": "ges_auth_token-deliverr-logistics:common",
        "get_token_url": "http://xmdfhq.nextsls.com/rest/tms/wos/auth/login",
        "get_data_url": "http://xmdfhq.nextsls.com/rest/tms/wos/shipment/lists",
        "view_url": "http://xmdfhq.nextsls.com/rest/tms/wos/shipment/view",
        "db_table": ods_scg_wld_logistics_trace_db_table,
        "create_table_query": ods_scg_wld_logistics_trace_table_i_d,
        "truncate_table_query": truncate_ods_scg_wld_logistics_trace_table_i_d,
        "table_field_list": ods_scg_wld_logistics_trace_table_i_d_field_list,
        "db_view": ods_scg_wld_logistics_trace_db_view,
        "create_view_query": ods_scg_wld_logistics_trace_view_i_d,
        "truncate_view_query": truncate_ods_scg_wld_logistics_trace_view_i_d,
        "view_field_list": ods_scg_wld_logistics_trace_view_i_d_field_list,
    },
    'AUASIAN': {
        "logistics_provider": "澳得亚物流",
        "hash_token_path": "crawler-deliverr-logistics:common",
        "token_key": "auasian_auth_token-deliverr-logistics:common",
        "get_token_url": "http://auasian.nextsls.com/rest/tms/wos/auth/login",
        "get_data_url": "http://auasian.nextsls.com/rest/tms/wos/shipment/lists",
        "view_url": "http://auasian.nextsls.com/rest/tms/wos/shipment/view",
        "db_table": ods_scg_wld_logistics_trace_db_table,
        "create_table_query": ods_scg_wld_logistics_trace_table_i_d,
        "truncate_table_query": truncate_ods_scg_wld_logistics_trace_table_i_d,
        "table_field_list": ods_scg_wld_logistics_trace_table_i_d_field_list,
        "db_view": ods_scg_wld_logistics_trace_db_view,
        "create_view_query": ods_scg_wld_logistics_trace_view_i_d,
        "truncate_view_query": truncate_ods_scg_wld_logistics_trace_view_i_d,
        "view_field_list": ods_scg_wld_logistics_trace_view_i_d_field_list,
    },
    'AAF': {
        "logistics_provider": "美通物流",
        "hash_token_path": "crawler-deliverr-logistics:common",
        "token_key": "aaf_auth_token-deliverr-logistics:common",
        "get_token_url": "http://aafxmx.nextsls.com/rest/tms/wos/auth/login",
        "get_data_url": "http://aafxmx.nextsls.com/rest/tms/wos/shipment/lists",
        "view_url": "http://aafxmx.nextsls.com/rest/tms/wos/shipment/view",
        "db_table": ods_scg_wld_logistics_trace_db_table,
        "create_table_query": ods_scg_wld_logistics_trace_table_i_d,
        "truncate_table_query": truncate_ods_scg_wld_logistics_trace_table_i_d,
        "table_field_list": ods_scg_wld_logistics_trace_table_i_d_field_list,
        "db_view": ods_scg_wld_logistics_trace_db_view,
        "create_view_query": ods_scg_wld_logistics_trace_view_i_d,
        "truncate_view_query": truncate_ods_scg_wld_logistics_trace_view_i_d,
        "view_field_list": ods_scg_wld_logistics_trace_view_i_d_field_list,
    },
    'K5': {
        "logistics_provider": "天伟物流",
        "hash_token_path": "crawler-deliverr-logistics:common",
        "token_key": "tw_auth_token-deliverr-logistics:common",
        "get_token_url": "https://tw.kingtrans.net/nclient/Logon",
        "get_data_url": "https://tw.kingtrans.net/nclient/CCOrder",
        "view_url": "http://aafxmx.nextsls.com/rest/tms/wos/shipment/view",
        "db_table": ods_scg_wld_tw_logistics_trace_db_table,
        "create_table_query": ods_scg_wld_tw_logistics_trace_table_i_d,
        "truncate_table_query": truncate_ods_scg_wld_tw_logistics_trace_table_i_d,
        "table_field_list": ods_scg_wld_tw_logistics_trace_table_i_d_field_list,
        "db_view": None,
        "create_view_query": None,
        "truncate_view_query": None,
        "view_field_list": None,
    },
    'AHC': {
        "logistics_provider": "快驿通",
        "hash_token_path": "crawler-deliverr-logistics:common",
        "token_key": "ahc_auth_token-deliverr-logistics:common",
        "get_token_url": "http://8.134.39.115:8000/cms/user/login",
        "get_data_url": "http://8.134.39.115:8000/cms/tpl/list/values",
        "view_url": "http://aafxmx.nextsls.com/rest/tms/wos/shipment/view",
        "db_table": ods_scg_wld_logistics_ahc_table,
        "create_table_query": ods_scg_wld_logistics_trace_table_i_d,
        "table_field_list": ods_scg_wld_logistics_trace_table_i_d_field_list,
        "truncate_table_query": None,
        "db_view": ods_scg_wld_logistics_trace_db_view,
        "create_view_query": ods_scg_wld_logistics_trace_view_i_d,
"truncate_view_query": None,
        "view_field_list": ods_scg_wld_logistics_trace_view_i_d_field_list,
    },
    'ZTO': {
        "logistics_provider": "中通",
        "hash_token_path": "crawler-deliverr-logistics:common",
        "token_key": "zto_auth_token-deliverr-logistics:common",
        "get_token_url": "http://112.74.95.234:9999/logon/checkLogon",
        "get_data_url": "http://112.74.95.234:9999/admin/waybill/order/orderList",
        "view_url": "http://aafxmx.nextsls.com/rest/tms/wos/shipment/view",
        "db_table": ods_scg_wld_logistics_ahc_table,
        "create_table_query": ods_scg_wld_logistics_trace_table_i_d,
        "table_field_list": ods_scg_wld_logistics_trace_table_i_d_field_list,
        "truncate_table_query": None,
        "db_view": ods_scg_wld_logistics_trace_db_view,
        "create_view_query": ods_scg_wld_logistics_trace_view_i_d,
        "truncate_view_query": None,
        "view_field_list": ods_scg_wld_logistics_trace_view_i_d_field_list,
    },
}
# LogisticsProviders = 'GES'
# # print(Fetcher_info[LogisticsProviders]['db_table'])
