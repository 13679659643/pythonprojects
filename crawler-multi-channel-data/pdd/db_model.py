# -*- coding: utf-8 -*-
# @Time    : 2024/11/26 9:30
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software: 数据库sql语句配置文件

# ODS-crawler-multi-channel-pdd-traffic:
ods_cd_sl_pdd_traffic_db_table = "ods_prod.ods_cd_sl_pdd_traffic_i_d"

ods_cd_sl_pdd_traffic_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_pdd_traffic_i_d`
(
    `dt`            varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `account`       varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '账户名',
    `uv`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '店铺访客数',
    `pv`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '店铺浏览量',
    `guv`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '商品访客数',
    `gpv`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '商品浏览量',
    `cfmOrdrUsrCnt` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交买家数',
    `cfmOrdrCnt`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交订单数',
    `cfmOrdrAmt`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交金额',
    `cfmUvRto`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '当天成交转化率',
    `cfmOrdrAup`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '客单价',
    `uvCfmVal`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '当天成交UV价值',
    PRIMARY KEY (`dt`, `account`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='朗盟拼多多-流量数据-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_pdd_traffic_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_pdd_traffic_i_d"

ods_cd_sl_pdd_traffic_i_d_field_list = [
    "dt",
    "account",
    "uv",
    "pv",
    "guv",
    "gpv",
    "cfmOrdrUsrCnt",
    "cfmOrdrCnt",
    "cfmOrdrAmt",
    "cfmUvRto",
    "cfmOrdrAup",
    "uvCfmVal",
]

# ODS-crawler-multi-channel-pdd-sales:
ods_cd_sl_pdd_sales_db_table = "ods_prod.ods_cd_sl_pdd_sales_i_d"

ods_cd_sl_pdd_sales_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_pdd_sales_i_d`
(
    `dt`               varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `account`          varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '账户名',
    `pltInvlOrdrCnt1m` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '介入订单数',
    `pltInvlOrdrRto1m` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '平台介入率',
    `sucRfOrdrCnt1d`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成功退款订单数',
    `sucRfOrdrAmt1d`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成功退款金额',
    `rfSucRto1m`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成功退款率',
    PRIMARY KEY(`dt`,`account`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='朗盟拼多多-服务数据-售后数据—成功退款金额-辜涛'
    partition by key(dt) partitions 3;
"""

truncate_ods_cd_sl_pdd_sales_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_pdd_sales_i_d"

ods_cd_sl_pdd_sales_i_d_field_list = [
    "dt",
    "account",
    "pltInvlOrdrCnt1m",
    "pltInvlOrdrRto1m",
    "sucRfOrdrCnt1d",
    "sucRfOrdrAmt1d",
    "rfSucRto1m",
]

# ODS-crawler-multi-channel-pdd-promotional:
ods_cd_sl_pdd_promotional_db_table = "ods_prod.ods_cd_sl_pdd_promotional_i_d"

ods_cd_sl_pdd_promotional_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_pdd_promotional_i_d`
(
    `dt`               varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `account`          varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '账户名',
    `spend`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总花费(元)',
    `liveCostPerOrder` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '每笔成交花费(元)',
    `orderSpend`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交花费(元)',
    `avgPayAmount`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '每笔成交金额(元)',
    `gmv`              varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '交易额(元)',
    `globalTakeRate`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '全站推广费比',
    `orderSpendRoi`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '实际投产比',
    `impression`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '曝光量',
    `orderNum`         varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交笔数',
    `click`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '点击量',
    PRIMARY KEY (`dt`, `account`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='朗盟拼多多-推广平台-商品推广-总花费-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_pdd_promotional_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_pdd_promotional_i_d"

ods_cd_sl_pdd_promotional_i_d_field_list = [
    "dt",
    "account",
    "spend",
    "liveCostPerOrder",
    "orderSpend",
    "avgPayAmount",
    "gmv",
    "globalTakeRate",
    "orderSpendRoi",
    "impression",
    "orderNum",
    "click",
]


