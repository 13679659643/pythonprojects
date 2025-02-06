# -*- coding: utf-8 -*-
# @Time    : 2024/11/26 9:30
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software: 数据库sql语句配置文件

# ODS-crawler-multi-channel-jd-jm:
ods_cd_sl_jd_jm_transaction_db_table = "ods_prod.ods_cd_sl_jd_jm_transaction_i_d"

ods_cd_sl_jd_jm_transaction_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_jm_transaction_i_d`
(
    `dt`            varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '日期',
    `account`       varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '账户名',
    `UV`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '访客数',
    `PV`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '浏览量',
    `AvgDepth`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '人均浏览量(每个访客平均浏览页面的数量)',
    `AvgStayTime`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '平均停留时长(秒,仅浏览店铺内页面1次就离开店铺的访客占总访客的比例。)',
    `SkipOut`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '跳失率(仅浏览店铺内页面1次就离开店铺的访客占总访客的比例。)',
    `OrderCustNum`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '下单客户数(去重后)',
    `OrderNum`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '下单单量',
    `OrderAmt`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '下单金额',
    `OrderProNum`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '下单商品件数(客户在店铺内成功下单订单中的商品件数，包含包括赠品在内的所有店内的商品。)',
    `OrdCustNum`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交客户数(去重后)',
    `OrdNum`        varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交单量',
    `OrdAmt`        varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交金额',
    `OrdProNum`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交商品件数(客户在店铺内成功下单且成交的商品件数，包含包括赠品在内的所有店内的商品。)',
    `UnitPriceAvg`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '件单价(成交金额/成交商品件数)',
    `CustPriceAvg`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '客单价',
    `CancelOrdAmt`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '取消及售后退款金额',
    `CancelSaleQty` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '取消及售后退款件数',
    `CancelOrdQty`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '取消及售后退款单量',
    PRIMARY KEY (`dt`, `account`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京麦-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_jm_transaction_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_jm_transaction_i_d"

ods_cd_sl_jd_jm_transaction_i_d_field_list = [
    "dt",
    "account",
    "UV",
    "PV",
    "AvgDepth",
    "AvgStayTime",
    "SkipOut",
    "OrderCustNum",
    "OrderNum",
    "OrderAmt",
    "OrderProNum",
    "OrdCustNum",
    "OrdNum",
    "OrdAmt",
    "OrdProNum",
    "UnitPriceAvg",
    "CustPriceAvg",
    "CancelOrdAmt",
    "CancelSaleQty",
    "CancelOrdQty",
]

# ODS-crawler-multi-channel-jd-jm-adaccounttotal:
ods_cd_sl_jd_jm_adaccounttotal_db_table = "ods_prod.ods_cd_sl_jd_jm_adaccounttotal_i_d"

ods_cd_sl_jd_jm_adaccounttotal_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_jm_adaccounttotal_i_d`
(
    `dt`            varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `account`       varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '账户名',
    `cost`          varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '花费',
    `impressions`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '展现数',
    `clicks`        varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '点击数',
    `CTR`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '点击率(%)',
    `CPM`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '千次展现成本',
    `CPC`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '平均点击成本',
    `totalOrderCnt` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总订单行',
    `totalOrderSum` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总订单金额',
    `totalOrderCVS` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '转化率(%)',
    `totalOrderROI` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '投产比',
    `clickDate`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'clickDate',
    PRIMARY KEY (`dt`, `account`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京麦京准通-搜推广告概况-账户汇总-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_jm_adaccounttotal_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_jm_adaccounttotal_i_d"

ods_cd_sl_jd_jm_adaccounttotal_i_d_field_list = [
    "dt",
    "account",
    "cost",
    "impressions",
    "clicks",
    "CTR",
    "CPM",
    "CPC",
    "totalOrderCnt",
    "totalOrderSum",
    "totalOrderCVS",
    "totalOrderROI",
    "clickDate",
]

# ODS-crawler-multi-channel-jd-jm-salestotal:
ods_cd_sl_jd_jm_salestotal_db_table = "ods_prod.ods_cd_sl_jd_jm_salestotal_i_d"

ods_cd_sl_jd_jm_salestotal_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_jm_salestotal_i_d`
(
    `dt`             varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `account`       varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '账户名',
    `cost`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '花费',
    `swaOrderROI`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '全站投产比',
    `swaOrderSum`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '全站交易额',
    `swaOrderCnt`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '全站订单行',
    `swaOrderCPA`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '全站订单成本',
    `swaOrderCPO`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '全站费比',
    `swaImpressions` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '核心位置展现量',
    `swaClicks`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '核心位置点击量',
    `date`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'date',
    `clickDate`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'clickDate',
    `totalOrderSum`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'totalOrderSum',
    `totalOrderROI`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'totalOrderROI',
    `totalOrderCnt`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'totalOrderCnt',
    `orderCPA`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'orderCPA',
    `totalOrderCPO`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'totalOrderCPO',
    `impressions`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'impressions',
    `clicks`         varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'clicks',
    PRIMARY KEY (`dt`, `account`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京麦京准通-全站营销概况-账户汇总-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_jm_salestotal_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_jm_salestotal_i_d"

ods_cd_sl_jd_jm_salestotal_i_d_field_list = [
    "dt",
    "account",
    "cost",
    "swaOrderROI",
    "swaOrderSum",
    "swaOrderCnt",
    "swaOrderCPA",
    "swaOrderCPO",
    "swaImpressions",
    "swaClicks",
    "date",
    "clickDate",
    "totalOrderSum",
    "totalOrderROI",
    "totalOrderCnt",
    "orderCPA",
    "totalOrderCPO",
    "impressions",
    "clicks",
]

# ODS-crawler-multi-channel-jd-jm-paymentcommissions:
ods_cd_sl_jd_jm_paymentcommissions_db_table = "ods_prod.ods_cd_sl_jd_jm_paymentcommissions_i_d"

ods_cd_sl_jd_jm_paymentcommissions_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_jm_paymentcommissions_i_d`
(
    `dt`           varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `account`      varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '账户名',
    `repDate`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'repDate',
    `cptCosFee`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '付款佣金(查询时间段内，已完成且有效订单的佣金支出，与实际扣费金额会有一定差异)',
    `inOrderCount` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '下单订单量(查询时间段内，下单且有效的子订单的数量)',
    `inCosPrice`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '下单订单金额(查询时间段内，下单且有效的订单中用户实际支付金额（不含运费）的汇总)',
    `inCosFee`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '预估商品佣金',
    `cartCount`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总加购数(总加购数)',
    `clickCount`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '商详点击数(查询时间段内，推广的链接（除抖快小店计划外）的点击数量)',
    `newPinCount`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'newPinCount',
    `roi`          varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'roi(查询时间段内，推广的链接（除抖快小店计划外）的点击数量)',
    PRIMARY KEY (`dt`, `account`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京麦京准通-京东联盟-选择日期-付款佣金-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_jm_paymentcommissions_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_jm_paymentcommissions_i_d"

ods_cd_sl_jd_jm_paymentcommissions_i_d_field_list = [
    "dt",
    "account",
    "repDate",
    "cptCosFee",
    "inOrderCount",
    "inCosPrice",
    "inCosFee",
    "cartCount",
    "clickCount",
    "newPinCount",
    "roi",
]