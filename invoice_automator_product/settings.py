# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 15:35
# @Author  : Night
# @File    : settings.py
# @Description:
# ---------------------------- project 配置 ----------------------------
PROJECT_NAME = "invoice_automator_product"
# 补全项目名称(一定要写)
PROJECT_TITLE = "发票自动化制作"
# 接口路由
prefix = f"/api/v1/{PROJECT_NAME}/schedule"

# 易搭同步运行标识符
redis_crawler_run_sign = PROJECT_NAME + ":run_sign" + ":yida_{}"

# tidb 数据同步
dim_invoice_amz_tracking_code = "dim_prod.dim_gsm_yida_invoice_amz_tracking_code_i_manual"
dim_invoice_amz_tracking_code_field_list = ["shipment_id", "amazon_tracking_code", "status"]

ods_gsm_lx_fba_shipment_carton_i_h = "ods_prod.ods_gsm_lx_fba_shipment_carton_i_h"
ods_gsm_lx_fba_shipment_carton_i_field_list = ['address1', 'address2', 'are_cases_required', 'label_prep_type',
                                               'delivery_order', 'city', 'district_or_county', 'create_date',
                                               'ship_to_name', 'ship_to_address', 'ship_to_city',
                                               'ship_to_province_code', 'ship_to_country', 'ship_to_country_code',
                                               'ship_to_postal_code', 'ship_to_address2', 'ship_to_district_or_county',
                                               'packaging_type', 'destination_fulfillment_center_id', 'id', 'is_closed',
                                               'ism_index', 'name', 'name_cn', 'name_en', 'phone', 'seller_name',
                                               'postal_code', 'shipment_id', 'shipment_name', 'shipment_status', 'sids',
                                               'state_or_province_code', 'status', 'uid', 'username', 'is_uploaded_box',
                                               'uploaded_box_user_id', 'uploaded_box_user', 'uploaded_box_time',
                                               'is_put_transport_content', 'put_transport_content_user_id',
                                               'put_transport_content_user', 'put_transport_content_time',
                                               'is_print_label', 'print_label_user_id', 'print_label_user',
                                               'print_label_time', 'is_marked_as_shipped', 'marked_as_shipped_user',
                                               'marked_as_shipped_user_id', 'marked_as_shipped_time', 'carton_excel_id',
                                               'carton_excel_url', 'carton_excel_name', 'print_box_label_num',
                                               'print_card_label_num', 'is_synchronous', 'create_by_erp',
                                               'last_success_box_count', 'remark', 'reference_id', 'is_sta',
                                               'ship_mode', 'box_type', 'is_shipto_diff', 'pdf_shipto_data',
                                               'to_closed_time', 'is_save_box', 'box_commit', 'staging', 'carton_type',
                                               'commit_excel_file_id', 'need_exp_date',
                                               'is_update_trans_after_upload_box', 'is_auto_transport_number',
                                               'is_can_update_shipped_box', 'upload_box_type',
                                               'is_support_partner_trans', 'partner_trans_country_code', 'is_staging',
                                               'is_open_ltl']

# fba装箱列表

dwd_scg_wld_lx_fba_shipment_box_detail_i_d = 'dwd_prod.dwd_scg_wld_lx_fba_shipment_box_detail_a_d'
dwd_scg_wld_lx_fba_shipment_box_detail_i_field_list = ['dt', 'shipment_id', 'address1', 'address2',
                                                       'are_cases_required', 'box_commit',
                                                       'carton_excel_id', 'carton_excel_name', 'carton_excel_url',
                                                       'carton_type', 'city',
                                                       'commit_excel_file_id', 'create_by_erp', 'create_date',
                                                       'delivery_order',
                                                       'destination_fulfillment_center_id', 'district_or_county', 'id',
                                                       'is_auto_transport_number',
                                                       'is_can_update_shipped_box', 'is_closed', 'is_marked_as_shipped',
                                                       'is_open_ltl',
                                                       'is_print_label',
                                                       'is_put_transport_content', 'is_save_box', 'is_shipto_diff',
                                                       'is_sta', 'is_staging',
                                                       'is_support_partner_trans', 'is_synchronous',
                                                       'is_update_trans_after_upload_box',
                                                       'is_uploaded_box', 'ism_index', 'label_prep_type',
                                                       'last_success_box_count',
                                                       'marked_as_shipped_time', 'marked_as_shipped_user',
                                                       'marked_as_shipped_user_id', 'name',
                                                       'name_cn', 'name_en', 'need_exp_date', 'packaging_type',
                                                       'partner_trans_country_code',
                                                       'pdf_shipto_data', 'phone', 'postal_code',
                                                       'print_box_label_num', 'print_card_label_num',
                                                       'print_label_time', 'print_label_user',
                                                       'print_label_user_id', 'put_transport_content_time',
                                                       'put_transport_content_user',
                                                       'put_transport_content_user_id', 'reference_id', 'remark',
                                                       'seller_name', 'ship_to_address',
                                                       'ship_to_address2', 'ship_to_city', 'ship_to_country',
                                                       'ship_to_country_code',
                                                       'ship_to_district_or_county', 'ship_to_name',
                                                       'ship_to_postal_code', 'ship_to_province_code',
                                                       'shipment_info', 'shipment_name', 'shipment_status', 'sids',
                                                       'staging',
                                                       'state_or_province_code', 'status', 'to_closed_time', 'uid',
                                                       'upload_box_type',
                                                       'uploaded_box_time', 'uploaded_box_user', 'uploaded_box_user_id',
                                                       'username']
dwd_scg_wld_lx_fba_shipment_box_detail_item_i_d = 'dwd_prod.dwd_scg_wld_lx_fba_shipment_box_detail_item_i_d'
dwd_scg_wld_lx_fba_shipment_box_detail_item_i__field_d = ['dt', 'shipment_id', 'box_id', 'length', 'width', 'height',
                                                          'weight', 'packed', 'fnsku', 'msku',
                                                          'quantity_shipped', 'exp_date', 'num']

# 钉钉 监控服务消息
dingding_api = 'https://oapi.dingtalk.com/robot/send?access_token=3f296e744bfdfd5f2694078a9d4e9b6793576c4fc441793b760be744335fd343'

dingding_group_api = 'https://oapi.dingtalk.com/robot/send?access_token=822bb8f13af4ae3fbb8883b490486eeb23587d9adcd4e3ab1a6e72015ee0a8e7'

# redis 图片链接
redis_img_key = PROJECT_NAME + ":run_sign" + ":img_key:"

# redis 货件信息运行标识
redis_fba_info_key = PROJECT_NAME + ":run_sign" + ":fba_info"

USERID = '16566389302394979'

appType = 'APP_VWP5WMVB2BLM0IP7IXDY'

systemToken = '7C766871KQABVU4770F6ZCMOZQE43XXSFGFIL92'

# fba货件列表
fba_shipment_list_api = 'https://erp.lingxing.com/api/fba_shipment/showShipment_v2?'

# fba发货单详情装箱
fba_shipment_box_api = 'https://erp.lingxing.com/api/fba_shipment/getCartonDetail'
