# -*- coding: utf-8 -*-
# @Time : 2023/11/15
# @Author : night
# @Email :
# @File :
# @desc :
crawler_lx_platform_wfs_stock_db_table = 'ods_prod.ods_cd_inv_wfs_stock_i_d'

ods_cd_inv_wfs_stock_i_d = """
CREATE TABLE if not exists ods_prod.ods_cd_inv_wfs_stock_i_d
(
    dt                         varchar(10)  NOT NULL COMMENT 'dt',
    id                         varchar(60)  NOT NULL COMMENT 'id',
    companyId                  varchar(60)  NOT NULL COMMENT '公司id',
    sid                        varchar(60)  NOT NULL COMMENT '店铺sid',
    warehouseUniqueId          varchar(60)  NOT NULL COMMENT '仓id',
    warehouseName              varchar(60)  NOT NULL COMMENT '仓库名',
    msku                       varchar(60)  NOT NULL COMMENT 'msku',
    gtin                       varchar(60)  NOT NULL COMMENT 'gtin',
    productUniqueId            varchar(60)  NOT NULL,
    itemId                     varchar(60)  NOT NULL COMMENT 'itemid',
    productName                varchar(60)  NOT NULL COMMENT '品名',
    sku                        varchar(60)  NOT NULL COMMENT 'sku',
    platformProductStatus      varchar(60)  NOT NULL COMMENT '在售状态',
    quantity                   varchar(10)  NOT NULL COMMENT '总库存',
    availableQuantity          varchar(10)  NOT NULL COMMENT 'WFS可售',
    unabledWarehousingQuantity varchar(10)  NOT NULL COMMENT '无法入库',
    inboundQuantity            varchar(10)  NOT NULL COMMENT '标发在途',
    damagedQuantity            varchar(10)  NOT NULL,
    ats03Months                varchar(10)  NOT NULL COMMENT '3个月库龄',
    ats36Months                varchar(10)  NOT NULL COMMENT '3-6个月库龄',
    ats69Months                varchar(10)  NOT NULL COMMENT '6-9个月库龄',
    ats912Months               varchar(10)  NOT NULL COMMENT '9-12月库龄',
    ats1Years                  varchar(10)  NOT NULL COMMENT '12个月以上库龄',
    last30DaysUnitsReceived    varchar(10)  NOT NULL COMMENT '近30天入库',
    last30DaysPoUnits          varchar(10)  NOT NULL COMMENT '近30天计划入库',
    deleteFlag                 varchar(60)  NOT NULL,
    gmtCreate                  varchar(60)  NOT NULL,
    gmtModified                varchar(60)  NOT NULL,
    picUrl                     varchar(300) NOT NULL COMMENT '图片链接',
    purchasePrice              varchar(15)  NOT NULL COMMENT '单价',
    pid                        varchar(20)  NOT NULL COMMENT 'pid',
    PRIMARY KEY (dt, msku, sid)
) COMMENT ='领星多平台-平台仓-WFS库存'
    partition by key (dt) partitions 3;
                    """

ods_cd_inv_wfs_stock_i_d_field_list = ['dt', 'id', 'companyId', 'sid', 'warehouseUniqueId', 'warehouseName', 'msku',
                                       'gtin', 'productUniqueId', 'itemId', 'productName', 'sku',
                                       'platformProductStatus', 'quantity', 'availableQuantity',
                                       'unabledWarehousingQuantity', 'inboundQuantity', 'damagedQuantity',
                                       'ats03Months', 'ats36Months', 'ats69Months', 'ats912Months', 'ats1Years',
                                       'last30DaysUnitsReceived', 'last30DaysPoUnits', 'deleteFlag', 'gmtCreate',
                                       'gmtModified', 'picUrl', 'purchasePrice', 'pid']

crawler_lx_platform_fbc_stock_db_table = 'ods_prod.ods_cd_inv_fbc_stock_i_d'

ods_cd_inv_fbc_stock_i_d = """
create table if not exists ods_prod.ods_cd_inv_fbc_stock_i_d
(
    dt                    varchar(10) not null comment 'dt',
    companyId             varchar(60) not null comment '公司id',
    sid                   varchar(60) not null comment '店铺sid',
    warehouseId           varchar(60) not null comment '仓库id',
    locationId            varchar(60) not null comment '位置id',
    warehouseName         varchar(60) not null comment '仓名称',
    warehouseUniqueId     varchar(60) not null comment '仓唯一id',
    productUniqueId       varchar(60) not null comment '产品id',
    msku                  varchar(60) not null comment 'msku',
    itemId                varchar(60) not null comment '产品id',
    productName           varchar(60) not null comment '品名',
    sku                   varchar(60) not null comment 'sku',
    title                 varchar(60) not null comment '标题',
    platformProductStatus varchar(60) not null comment '商品状态',
    quantity              varchar(60) not null comment '总库存',
    quantityCost          varchar(60) not null comment '',
    picUrl                varchar(60) not null comment '',
    purchasePrice         varchar(60) not null comment '',
    pid                   varchar(60) not null comment '',
    gmtCreate             varchar(60) not null comment '',
    gmtModified           varchar(60) not null comment '',
    availableQuantity     varchar(60) not null comment 'FBC可售',
    removalQuantity       varchar(60) not null comment '移除库存',
    litigationQuantity    varchar(60) not null comment '争议库存',
    returnQuantity        varchar(60) not null comment '退货',
    blockedQuantity       varchar(60) not null comment '已冻结',
    allocatedQuantity     varchar(60) not null comment '调仓中',
    primary key (dt, msku, sid,itemId)
) comment = '平台仓-CD库存'
    partition by key (dt) partitions 3;
                    """

ods_cd_inv_fbc_stock_i_d_field_list = ['dt', 'companyId', 'sid', 'warehouseId', 'locationId', 'warehouseName',
                                       'warehouseUniqueId', 'productUniqueId', 'msku', 'itemId', 'productName', 'sku',
                                       'title', 'platformProductStatus', 'quantity', 'quantityCost', 'picUrl',
                                       'purchasePrice', 'pid', 'gmtCreate', 'gmtModified', 'availableQuantity',
                                       'removalQuantity', 'litigationQuantity', 'returnQuantity', 'blockedQuantity',
                                       'allocatedQuantity']

ods_gsm_lx_mp_platform_wh_shipment_i_h = "ods_prod.ods_gsm_lx_mp_platform_wh_shipment_i_h"
ods_gsm_lx_mp_platform_wh_shipment_field_list = [
    "dt",
    "id",
    "shippingListCode",
    "warehouseId",
    "platformCode",
    "warehouseName",
    "logisticsProviderId",
    "logisticsChannelId",
    "logisticsProviderName",
    "logisticsChannelName",
    "logisticsTypeName",
    "createUserId",
    "creator",
    "gmtCreate",
    "deliveryTime",
    "arrivalTime",
    "sailTime",
    "expectedArrivalTime",
    "actualDueTime",
    "orderLogisticsStatus",
    "actualDeliveryTime",
    "logisticsCode",
    "shippingListRemark",
    "shippingListStatus",
    "shippingListStatusDesc",
    "pickingStatus",
    "pickingStatusDesc",
    "storeId"
]

ods_gsm_lx_mp_platform_wh_shipment_detail_i_h = "ods_prod.ods_gsm_lx_mp_platform_wh_shipment_detail_i_h"
ods_gsm_lx_mp_platform_wh_shipment_detail_field_list = [
    "dt",
    "shippingListCode",
    "id",
    "goodsUrl",
    "platformCode",
    "platformName",
    "countryCode",
    "countryName",
    "storeId",
    "storeName",
    "cargoId",
    "cargoCode",
    "cargoGoodsId",
    "msku",
    "articleNumbering",
    "productId",
    "productName",
    "productType",
    "sku",
    "specId",
    "specInfo",
    "quantityInCase",
    "boxNum",
    "boxLength",
    "boxWidth",
    "boxHeight",
    "packageLength",
    "packageWidth",
    "packageHeight",
    "cbm",
    "cgProductNetWeight",
    "cgProductGrossWeight",
    "boxWeight",
    "boxNetWeight",
    "boxGrossWeight",
    "volumeWeight",
    "usableNum",
    "applyNum",
    "shipmentsNum",
    "totalNw",
    "totalGw",
    "taxAmount",
    "taxCurrency",
    "remark",
    "hasPair",
    "whbCodeInfo",
    "stockDeduct"
]
