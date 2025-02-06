# -*- coding: utf-8 -*-
# @Time    : 2024/11/26 9:30
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software: 数据库sql语句配置文件

# ODS-crawler-multi-channel-jd-vcp-performance:
ods_cd_sl_jd_performance_db_table = "ods_prod.ods_cd_sl_jd_performance_i_d"

ods_cd_sl_jd_performance_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_performance_i_d`
(
    `dt`                   varchar(50) COLLATE utf8mb4_general_ci  NOT NULL COMMENT '日期',
    `income`               varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '收入',
    `skuName`              varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '商品名称',
    `saleAmt`              varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'saleAmt',
    `cost`                 varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '成本',
    `fullMinusOfferAmount` varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '满返满减额',
    `cpsOffsetAmount`      varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '优惠券抵减数',
    `skuId`                varchar(50) COLLATE utf8mb4_general_ci  NOT NULL COMMENT '商品编码',
    `sales`                varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '财务销量',
    `grossProfit`          varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '毛利',
    `pointOffsetAmount`    varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '积分抵减数',
    `stockTurnoverDays`    varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '库存周转天数',
    PRIMARY KEY (`dt`, `skuId`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京东自营-辜涛';
"""

truncate_ods_cd_sl_jd_performance_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_performance_i_d"

ods_cd_sl_jd_performance_i_d_field_list = [
    "dt",
    "income",
    "skuName",
    "saleAmt",
    "cost",
    "fullMinusOfferAmount",
    "cpsOffsetAmount",
    "skuId",
    "sales",
    "grossProfit",
    "pointOffsetAmount",
    "stockTurnoverDays",
]

# ODS-crawler-multi-channel-jd-vcp-transaction:
ods_cd_sl_jd_transaction_db_table = "ods_prod.ods_cd_sl_jd_transaction_i_d"

ods_cd_sl_jd_transaction_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_transaction_i_d`
(
    `dt`           varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `Date`         varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '日期',
    `ShopType`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '类型',
    `ShopName`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '店铺名称',
    `BrandName`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '品牌',
    `CategoryName` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '类目',
    `ChannelName`  varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '终端',
    `PV`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '浏览量',
    `UV`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '访客数',
    `DealUser`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交人数',
    `DealNum`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交单量',
    `DealProNum`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交商品件数',
    `DealAmt`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '成交金额',
    `ShopId`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'ShopId',
    PRIMARY KEY (`dt`, `ChannelName`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京东自营交易明细-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_transaction_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_transaction_i_d"

ods_cd_sl_jd_transaction_i_d_field_list = [
    "dt",
    "Date",
    "ShopType",
    "ShopName",
    "BrandName",
    "CategoryName",
    "ChannelName",
    "PV",
    "UV",
    "DealUser",
    "DealNum",
    "DealProNum",
    "DealAmt",
    "ShopId",
]

# ODS-crawler-multi-channel-jd-jzt-adaccounttotal:
ods_cd_sl_jd_jzt_adaccounttotal_db_table = "ods_prod.ods_cd_sl_jd_jzt_adaccounttotal_i_d"

ods_cd_sl_jd_jzt_adaccounttotal_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_jzt_adaccounttotal_i_d`
(
    `dt`            varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
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
    PRIMARY KEY (`dt`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京东自营京准通-搜推广告概况-账户汇总-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_jzt_adaccounttotal_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_jzt_adaccounttotal_i_d"

ods_cd_sl_jd_jzt_adaccounttotal_i_d_field_list = [
    "dt",
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

# ODS-crawler-multi-channel-jd-jzt-salestotal:
ods_cd_sl_jd_jzt_salestotal_db_table = "ods_prod.ods_cd_sl_jd_jzt_salestotal_i_d"

ods_cd_sl_jd_jzt_salestotal_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_jzt_salestotal_i_d`
(
    `dt`             varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
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
    PRIMARY KEY (`dt`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京东自营京准通-全站营销概况-账户汇总-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_jzt_salestotal_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_jzt_salestotal_i_d"

ods_cd_sl_jd_jzt_salestotal_i_d_field_list = [
    "dt",
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

# ODS-crawler-multi-channel-jd-jzt-businessaccounttotal:
ods_cd_sl_jd_jzt_businessaccounttotal_db_table = "ods_prod.ods_cd_sl_jd_jzt_businessaccounttotal_i_d"

ods_cd_sl_jd_jzt_businessaccounttotal_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_jzt_businessaccounttotal_i_d`
(
    `dt`                varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `cost`              varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '花费',
    `impressions`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '展现数',
    `clicks`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '点击数',
    `CTR`               varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '点击率(%)',
    `CPM`               varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '千次展现成本',
    `CPC`               varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '平均点击成本',
    `totalPayOrderCnt`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总订单行(下单口径)',
    `totalDealOrderSum` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总订单金额(下单口径)',
    `totalDealOrderCnt` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总订单行(成交口径)',
    `totalPayOrderSum`  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总订单金额(成交口径)',
    `clickDate`         varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'clickDate',
    `uniqueImpressions` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'uniqueImpressions',
    `uniqueClicks`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'uniqueClicks',
    PRIMARY KEY (`dt`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-朗盟京东自营京淮通-B端营销-账户投放概况-账户汇总-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_jzt_businessaccounttotal_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_jzt_businessaccounttotal_i_d"

ods_cd_sl_jd_jzt_businessaccounttotal_i_d_field_list = [
    "dt",
    "cost",
    "impressions",
    "clicks",
    "CTR",
    "CPM",
    "CPC",
    "totalPayOrderCnt",
    "totalDealOrderSum",
    "totalDealOrderCnt",
    "totalPayOrderSum",
    "clickDate",
    "uniqueImpressions",
    "uniqueClicks",
]

# ODS-crawler-multi-channel-jd-fc-solidsales:
ods_cd_sl_jd_fc_solidsales_db_table = "ods_prod.ods_cd_sl_jd_fc_solidsales_i_d"

ods_cd_sl_jd_fc_solidsales_i_d ="""
CREATE TABLE IF NOT EXISTS ods_prod.`ods_cd_sl_jd_fc_solidsales_i_d`
(
    `dt`                varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '采集日期',
    `amount`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '总金额',
    `buyerName`         varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '采销员/销售员',
    `channelCode`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '采购渠道',
    `currency`          varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '币种',
    `goodsName`         varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '商品名称',
    `id`                varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT 'id',
    `orderNo`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '订单号',
    `ouName`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '合同主题',
    `poId`              varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '采购单号',
    `refDate`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '业务日期',
    `refId`             varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '单据编号',
    `refType`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '单据类型',
    `saleReturnNo`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '销售退货编号',
    `sku`               varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'sku',
    `skuNum`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'sku数量',
    `supplierId`        varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '供应商id',
    `channelName`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '渠道名称',
    `fcpyBillingAmount` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '账单金额',
    PRIMARY KEY (`dt`, `id`) /*T![clustered_index] CLUSTERED */
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='ODS-京东自营-财务管理-结算管理-实销实结明细-辜涛'
    partition by key (dt) partitions 3;
"""

truncate_ods_cd_sl_jd_fc_solidsales_i_d = "TRUNCATE TABLE ods_prod.ods_cd_sl_jd_fc_solidsales_i_d"

ods_cd_sl_jd_fc_solidsales_i_d_field_list = [
    "dt",
    "amount",
    "buyerName",
    "channelCode",
    "currency",
    "goodsName",
    "id",
    "orderNo",
    "ouName",
    "poId",
    "refDate",
    "refId",
    "refType",
    "saleReturnNo",
    "sku",
    "skuNum",
    "supplierId",
    "channelName",
    "fcpyBillingAmount",
]



