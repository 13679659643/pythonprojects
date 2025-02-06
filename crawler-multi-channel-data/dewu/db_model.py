# -*- coding: utf-8 -*-
# @Time    : 2024/12/10 17:40
# @Author  : Night
# @File    : db_model.py
# @Description:
ods_cd_sl_dw_closed_transaction_dashboard_db_table = "ods_prod.ods_cd_sl_dw_closed_transaction_dashboard_i_d"

ods_cd_sl_dw_closed_transaction_dashboard_i_d = """
create table if not exists ods_prod.ods_cd_sl_dw_closed_transaction_dashboard_i_d
(
    dt                    varchar(10) not null comment '交易日期',
    account               varchar(30) not null comment '用户账号',
    cancelAmount          varchar(20) not null comment '取消单金额',
    cancelOrderCnt        varchar(20) not null comment '取消单量',
    cancelRate            varchar(20) not null comment '订单取消占比',
    returnAmount          varchar(20) not null comment '退货订单金额',
    returnOrderCnt        varchar(20) not null comment '退货单量',
    returnRate            varchar(20) not null comment '退货订单占比',
    unpaidAmount          varchar(20) not null comment '未支付单金额',
    unpaidOrderCnt        varchar(20) not null comment '未支付单量',
    unpaidRate            varchar(20) not null comment '未支付订单占比',
    unperformanceAmount   varchar(20) not null comment '未履约订单金额',
    unperformanceOrderCnt varchar(20) not null comment '未履约单量',
    unperformanceRate     varchar(20) not null comment '未履约订单占比',
    primary key (dt, account)
) comment ='得物-交易分析-交易关闭看板-张致富'
    partition by key (dt) partitions 3;
"""
ods_cd_sl_dw_closed_transaction_dashboard_i_d_field_list = [
    "dt",
    "account",
    "cancelAmount",
    "cancelOrderCnt",
    "cancelRate",
    "returnAmount",
    "returnOrderCnt",
    "returnRate",
    "unpaidAmount",
    "unpaidOrderCnt",
    "unpaidRate",
    "unperformanceAmount",
    "unperformanceOrderCnt",
    "unperformanceRate",
]

ods_cd_sl_dw_transaction_overview_db_table = "ods_prod.ods_cd_sl_dw_transaction_overview_i_d"

ods_cd_sl_dw_transaction_overview_i_d = """
create table if not exists ods_prod.ods_cd_sl_dw_transaction_overview_i_d
(
    dt                    varchar(10) not null comment '交易日期',
    account               varchar(30) not null comment '用户账号',
    cancelAmount          varchar(20) not null comment '取消单金额',
    cancelOrderCnt        varchar(20) not null comment '取消单量',
    cancelRate            varchar(20) not null comment '订单取消占比',
    returnAmount          varchar(20) not null comment '退货订单金额',
    returnOrderCnt        varchar(20) not null comment '退货单量',
    returnRate            varchar(20) not null comment '退货订单占比',
    unpaidAmount          varchar(20) not null comment '未支付单金额',
    unpaidOrderCnt        varchar(20) not null comment '未支付单量',
    unpaidRate            varchar(20) not null comment '未支付订单占比',
    unperformanceAmount   varchar(20) not null comment '未履约订单金额',
    unperformanceOrderCnt varchar(20) not null comment '未履约单量',
    unperformanceRate     varchar(20) not null comment '未履约订单占比',
    primary key (dt, account)
) comment ='得物-交易分析-交易关闭看板-张致富'
    partition by key (dt) partitions 3;
"""
ods_cd_sl_dw_transaction_overview_i_d_field_list = [
    "dt",
    "account",
    "onlyPrdAccessUv",
    "paidAmount",
    "paidAvePricePerOrder",
    "paidBuyerCnt",
    "paidOrderCnt",
    "submitAmount",
    "submitBuyerCnt",
    "submitOrderCnt",
    "successAmount",
    "successAvePricePerOrder",
    "successOrderCnt",
]

ods_cd_sl_dw_ad_promotion_db_table = "ods_prod.ods_cd_sl_dw_ad_promotion_i_d"

ods_cd_sl_dw_ad_promotion_i_d = """
create table if not exists ods_prod.ods_cd_sl_dw_ad_promotion_i_d
(
    dt                   varchar(10) not null comment '交易日期',
    account              varchar(30) not null comment '用户账号',
    consumeFee           varchar(20) not null comment '消耗(元)',
    exposureCnt          varchar(20) not null comment '曝光(次)',
    clickCnt             varchar(20) not null comment '点击(次)',
    paymentOrder         varchar(20) not null comment '引导支付单量(单)',
    paymentAmt           varchar(20) not null comment '引导支付金额(元)',
    productRoi           varchar(20) not null comment '投产比ROI',
    clickRate            varchar(20) not null comment '点击率(%)',
    thousandexposureCost varchar(20) not null comment '千次曝光费用(元)',
    DepaymentOrderQty    varchar(20) not null comment '直接支付单量(单)',
    DepaymentAmt         varchar(20) not null comment '直接支付金额(元)',
    clickConversionRate  varchar(20) not null comment '点击转化率(%)',
    orderCost            varchar(20) not null comment '订单成本(元)',
    DeCollectOrderNumber varchar(20) not null comment '直接收藏预约数(次)',
    CollectOrderCost     varchar(20) not null comment '收藏预约成本(元)',
    primary key (dt, account)
) comment ='得物-营销-推广数据-张致富'
    partition by key (dt) partitions 3;
"""
ods_cd_sl_dw_ad_promotion_i_d_field_list = [
    "dt",
    "account",
    "consumeFee",
    "exposureCnt",
    "clickCnt",
    "paymentOrder",
    "paymentAmt",
    "productRoi",
    "clickRate",
    "thousandexposureCost",
    "DepaymentOrderQty",
    "DepaymentAmt",
    "clickConversionRate",
    "orderCost",
    "DeCollectOrderNumber",
    "CollectOrderCost"
]

ods_cd_sl_dw_gravity_drop_wallet_db_table = "ods_prod.ods_cd_sl_dw_gravity_drop_wallet_i_d"

ods_cd_sl_dw_gravity_drop_wallet_i_d = """
create table if not exists ods_prod.ods_cd_sl_dw_gravity_drop_wallet_i_d
(
    dt                 varchar(10)  not null comment '交易日期',
    account            varchar(30)  not null comment '用户账号',
    parent_id          varchar(20)  not null comment '父任务id',
    sub_id             varchar(20)  not null comment '子任务id',
    heating_name       varchar(200) not null comment '加热名称',
    order_time         varchar(30)  not null comment '下单时间',
    amt_transfer_time  varchar(30)  not null comment '金额流转时间',
    transaction_status varchar(30)  not null comment '交易状态',
    transaction_amt    varchar(20)  not null comment '交易金额',
    task_type          varchar(20)  not null comment '任务类型'
) comment ='得物-营销-引力投放-张致富'
    partition by key (dt) partitions 3;
"""
ods_cd_sl_dw_gravity_drop_wallet_i_d_field_list = [
    "dt",
    "account",
    "parent_id",
    "sub_id",
    "heating_name",
    "order_time",
    "amt_transfer_time",
    "transaction_status",
    "transaction_amt",
    "task_type",
]
