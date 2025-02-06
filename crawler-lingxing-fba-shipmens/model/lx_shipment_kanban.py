# _*_ coding: utf-8 _*_
# @Time : 2024/8/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-fba-shipmens
# @Desc :

# FBA货件看板
ods_scg_wld_lx_shipment_kanban = "ods_prod.ods_scg_wld_lx_shipment_kanban_i_h"
ods_scg_wld_lx_shipment_kanban_field_list = [
    "dt",
    "id",
    "shipment_id",
    "shipment_name",
    "sid",
    "mid",
    "destination_fulfillment_center_id",
    "reference_id",
    "reference_error_msg",
    "shipment_status",
    "reference_sync_status",
    "send_type",
    "remark",
    "to_closed_time",
    "create_date",
    "update_date",
    "application_total_num",
    "received_total_num",
    "send_total_num",
    "shipment_id_list",
    "sname",
    "country_name",
    "application_diff_total_num",
    "received_diff_total_num",
    "application_received_diff",
    "logistics_status_type_name",
    "logistics_status_time"
]

# FBA货件看板详情
ods_scg_wld_lx_shipment_kanban_item = "ods_prod.ods_scg_wld_lx_shipment_kanban_item_i_h"
ods_scg_wld_lx_shipment_kanban_item_field_list = [
    "shipment_id",
    "fnsku",
    "msku",
    "is_delete",
    "title",
    "product_name",
    "sku",
    "product_id",
    "product_mws_id",
    "application_total_num",
    "received_total_num",
    "send_total_num",
    "application_diff_total_num",
    "received_diff_total_num",
    "application_received_diff",
    "update_date",
    "is_combo",
    "product_image"
]