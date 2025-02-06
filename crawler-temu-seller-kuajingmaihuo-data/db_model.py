# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:

# temu-跨境卖家中心-店铺管理-违规信息

ods_cd_sl_temu_seller_illegalidata_i_d_db_table = "ods_prod.ods_cd_sl_temu_seller_illegalidata_i_d"

ods_cd_sl_temu_seller_illegalidata_i_d_field_list = [
    'dt',
    'violationAppealSn',
    'violationType',  # 1、延迟到货 2、虚假交易 3、异常轨迹 4、虚假发货 5、缺货 6、欺诈发货 8、加收运费违规
    'exceptionTypeList',  # 1、轨迹节点时间过早 2、异地签收 5、物流单号异常 0、其他
    'subTargetCount',
    'exceptedAmount',
    'actualAmount',
    'informTime',
    'lastAppealTime',
    'appealProgress',  # 0、待申述 1、待完善资料 2、平台处理中 3、处理完成 4、超时关闭申述
    'username',
    'mallId',
    'mallName'
]

# temu-跨境卖家中心-店铺管理-违规信息详情

ods_cd_sl_temu_seller_illegalidetail_i_d_db_table = "ods_prod.ods_cd_sl_temu_seller_illegalidetail_i_d"

ods_cd_sl_temu_seller_illegalidetail_i_d_field_list = [
    'violationAppealSn',
    'poNumber',
    'amount',
    'currency',
    'promiseTime',
    'violationType',
    'mallId',
    'mallName',
]

# temu-跨境卖家中心-商品管理-商品列表主要数据

dim_cd_sl_temu_seller_productlist_i_d_db_table = "dim_prod.dim_cd_sl_temu_seller_productlist_i_d"

dim_cd_sl_temu_seller_productlist_i_d_field_list = [
    'productId',
    'productSkcId',
    'productName',
    'extCode',
    'catName',
    'leafCat',
    'mainImageUrl',
    'siteName',
    'productProperties',
    'sizeTemplateIds',
    'instructioninfo',
    'createdAt',
]

# temu-跨境卖家中心-商品管理-商品列表明细数据

dim_cd_sl_temu_seller_productlist_details_i_d_db_table = "dim_prod.dim_cd_sl_temu_seller_productlist_details_i_d"

dim_cd_sl_temu_seller_productlist_details_i_d_field_list = [
    'productId',
    'productSkcId',
    'productSkuId',
    'productSkuSpecList',
    'productSkuShippingMode',
    'skuStockQuantity',
    'existShippingShelfRoute',
    'chineseName',
    'numberOfPieces',
    'supplierPrice',
    'productSkuVolume',
    'productSkuWeight',
    'extCode',
    'currencyType',
    'thumbUrl',
]

# temu-跨境卖家中心-店铺营销-营销活动-长期活动

ods_cd_sl_temu_seller_salesactlong_i_d_db_table = "ods_prod.ods_cd_sl_temu_seller_salesactlong_i_d"

ods_cd_sl_temu_seller_salesactlong_i_d_field_list = [
    'dt',
    'goodsId',
    'productName',
    'productId',
    'siteName',
    'pictureUrl',
    'skcId',
    'extCode',
    'skuattributeset',
    'dailyPrice',
    'activityPricemin',
    'activityPricemax',
    'suggestActivityPrice',
    'privilegeSuggestActivityPrice',
    'currency',
    'enrollTime',
    'activityTypeName',
    'activityThematicName',
    'sessionName',
    'startDateStr',
    'endDateStr',
    'durationDays',
    'sessionStatus',
    'activityStock',
    'remainingActivityStock',
    'suggestActivityStock',
    'mallName',
    'mallId',
]

# temu-跨境卖家中心-店铺营销-营销活动-专题活动

ods_cd_sl_temu_seller_thematicact_i_d_db_table = "ods_prod.ods_cd_sl_temu_seller_thematicact_i_d"

ods_cd_sl_temu_seller_thematicact_i_d_field_list = [
    'dt',
    'id',
    'name',
    'productId',
    'siteName',
    'pictureUrl',
    'skcId',
    'extCode',
    'skuattributeset',
    'dailyPrice',
    'activityPricemin',
    'activityPricemax',
    'targetActivityPrice',
    'currency',
    'signUpTime',
    'invitationTypeName',
    'activityName',
    'sessionName',
    'startDateStr',
    'endDateStr',
    'durationDays',
    'sessionStatus',
    'activityStock',
    'activityRemainStock',
    'suggestActivityStock',
    'mallName',
    'mallId'
]

# temu-跨境卖家中心-订单管理-订单列表-买家履约订单

ods_cd_sl_temu_seller_orderlist_i_d_db_table = "ods_prod.ods_cd_sl_temu_seller_orderlist_i_d"

ods_cd_sl_temu_seller_orderlist_i_d_field_list = [
    'dt',
    'parentOrderSn',
    'siteName',
    'regionName1',
    'parentOrderStatus',
    'extCodeList',
    'productSkuId',
    'productSkcId',
    'productSpuId',
    'productQuantity',
    'goodsName',
    'orderSn',
    'spec',
    'warehouseName',
    'thumbUrl',
    'shippedQuantity',
    'relatedGoodsInfoForAggregation',
    'parentOrderTimeStr',
    'parentOrderPendingEndTimeStr',
    'expectShipLatestTimeStr',
    'parentShippingTimeStr',
    'expectDeliveryEndTimeStr',
    'parentReceiptTimeStr',
    'mallName',
    'mallId',
]