# -*- coding: utf-8 -*-
# @Time    : 2024/12/16 14:32
# @Author  : Night
# @File    : db_model.py
# @Description:
ods_cd_sl_qn_promotion_amt_data_i_d_db_table = "ods_prod.ods_cd_sl_qn_promotion_amt_data_i_d"

ods_cd_sl_qn_promotion_amt_data_i_d = """
create table if not exists ods_prod.ods_cd_sl_qn_promotion_amt_data_i_d
(
    dt             varchar(10)  not null comment '交易日期',
    account        varchar(30)  not null comment '用户账号',
    amount         varchar(20)  not null comment '操作金额',
    balance        varchar(20)  not null comment '操作后余额',
    batchno        varchar(200) not null comment '',
    bizType        varchar(30)  not null comment '',
    comment        varchar(200) not null comment '备注',
    finType        varchar(30)  not null comment '收支类型( 1.CREDIT(支出) 2.DEBIT(收入) )',
    memberId       varchar(20)  not null comment '成员id',
    orderDetail    varchar(20)  not null comment '订单详情',
    relationId     varchar(20)  not null comment '关系id',
    showDetail     varchar(20)  not null comment '展示详情',
    total          varchar(20)  not null comment '总共',
    tradeJournalId varchar(20)  not null comment '交易id',
    tradeType      varchar(20)  not null comment '交易类型( 1.DEDUCT(扣款) 2.CHARGE(充值) )',
    transTime      varchar(20)  not null comment '交易日期',
    uniTransTime   varchar(30)  not null comment '记账日期',
    primary key (dt, account, finType)
) comment ='千牛-推广中心-账户明细-张致富'
    partition by key (dt) partitions 3;
"""
ods_cd_sl_qn_promotion_amt_data_i_d_field_list = [
    'dt',
    'account',
    'amount',
    'balance',
    'batchno',
    'bizType',
    'comment',
    'finType',
    'memberId',
    'orderDetail',
    'relationId',
    'showDetail',
    'total',
    'tradeJournalId',
    'tradeType',
    'transTime',
    'uniTransTime',
]

ods_cd_sl_qn_operation_win_data_i_d_db_table = "ods_prod.ods_cd_sl_qn_operation_win_data_i_d"

ods_cd_sl_qn_operation_win_data_i_d = """
create table if not exists ods_prod.ods_cd_sl_qn_operation_win_data_i_d
(
    dt               varchar(10) not null comment '采集日期',
    account          varchar(30) not null comment '用户账号',
    adStrategyAmt    varchar(20) not null comment '智能场景花费',
    admCostFamtQzt   varchar(20) not null comment '全站推广花费',
    cartByrCnt       varchar(20) not null comment '加购人数',
    cartCnt          varchar(20) not null comment '加购件数',
    cartItemCnt      varchar(20) not null comment '加购件数',
    cltItmCnt        varchar(20) not null comment '商品收藏人数',
    cubeAmt          varchar(20) not null comment '精准人群推广花费',
    descScore        varchar(20) not null comment '',
    feedCharge       varchar(20) not null comment '',
    oldRepeatByrRate varchar(20) not null comment '老客复购率',
    olderPayAmt      varchar(20) not null comment '老买家支付金额',
    p4pExpendAmt     varchar(20) not null comment '关键词推广花费',
    payAmt           varchar(20) not null comment '支付金额',
    payByrCnt        varchar(20) not null comment '支付买家数',
    payItmCnt        varchar(20) not null comment '支付件数',
    payOldByrCnt     varchar(20) not null comment '支付老买家数',
    payOrdByrCnt365  varchar(20) not null comment '支付老买家数(365天)',
    payOrdCnt        varchar(20) not null comment '支付子订单数',
    payPct           varchar(20) not null comment '客单价',
    payRate          varchar(20) not null comment '支付转化率',
    pv               varchar(20) not null comment '浏览量',
    rfdSucAmt        varchar(20) not null comment '成功退款金额',
    stayTime         varchar(20) not null comment '',
    subPayOrdAmt     varchar(20) not null comment '支付金额',
    subPayOrdSubCnt  varchar(20) not null comment '支付子订单数',
    tkExpendAmt      varchar(20) not null comment '淘宝客佣金',
    uv               varchar(20) not null comment '访客数',
    zzExpendAmt      varchar(20) not null comment '',
    primary key (dt, account)
) comment ='千牛-运营视窗-数据看板-张致富'
    partition by key (dt) partitions 3;
"""
ods_cd_sl_qn_operation_win_data_i_d_field_list = [
    'dt',
    'account',
    'adStrategyAmt',
    'admCostFamtQzt',
    'cartByrCnt',
    'cartCnt',
    'cartItemCnt',
    'cltItmCnt',
    'cubeAmt',
    'descScore',
    'feedCharge',
    'oldRepeatByrRate',
    'olderPayAmt',
    'p4pExpendAmt',
    'payAmt',
    'payByrCnt',
    'payItmCnt',
    'payOldByrCnt',
    'payOrdByrCnt365',
    'payOrdCnt',
    'payPct',
    'payRate',
    'pv',
    'rfdSucAmt',
    'stayTime',
    'subPayOrdAmt',
    'subPayOrdSubCnt',
    'tkExpendAmt',
    'uv',
    'zzExpendAmt',
]

ods_cd_sl_qn_order_management_data_i_d_db_table = "ods_prod.ods_cd_sl_qn_order_management_data_i_d"

ods_cd_sl_qn_order_management_data_i_d = """
create table if not exists ods_prod.ods_cd_sl_qn_order_management_data_i_d
(
    dt        varchar(10) not null comment '付款日期',
    account   varchar(30) not null comment '用户账号',
    id        varchar(30) not null comment '订单号',
    currency  varchar(20) not null comment '币种',
    actualFee varchar(20) not null comment '实收款',
    postType  varchar(20) not null comment '含快递',
    text      varchar(60) not null comment '交易状态',
    quantity  varchar(20) not null comment '数量',
    realTotal varchar(20) not null comment '单价',
    primary key (dt, account, id)
) comment ='千牛-订单管理交易-张致富'
    partition by key (dt) partitions 3;
"""
ods_cd_sl_qn_order_management_data_i_d_field_list = [
    'dt',
    'account',
    'id',
    'currency',
    'actualFee',
    'postType',
    'text',
    'quantity',
    'realTotal',
]
