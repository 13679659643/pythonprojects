# -*- coding: utf-8 -*-
# @Time    : 2023/11/15
# @Author  : night
# @Email   :
# @File    : 
# @Software: 配置文件
# ---------------------------- project 配置 ----------------------------


PROJECT_NAME = "crawler-lingxing-platform-warehouse-data"
# 补全项目名称(一定要写)
PROJECT_TITLE = "领星多平台数据采集服务(爬虫)"
# 接口路由
prefix = f"/api/v1/{PROJECT_NAME}/schedule"

AUTH_TOKEN = "common-lingxing-access-token:common:auth_tokens"

# 子服务
platform_wfs_stock = "crawler_lx_platform_wfs_stock"  # 领星多平台-平台仓-wfs(沃尔玛)

platform_fba_stock = "crawler_lx_platform_fbc_stock"  # 领星多平台-平台仓-fbc(cd)

# mongodb 配置
mongo_db = 'ods_crawler_lingxing'
mongo_db_table = 'ods_cd_inv_fbc_stock_i_d'
mongo_db_field = ['dt', 'msku', 'sid']

wfs_stock_url = "https://gw.lingxingerp.com/mp-platform-warehouse-api/api/walmart/walmartStockSearch"  # wfs

fbc_stock_url = "https://gw.lingxingerp.com/mp-platform-warehouse-api/api/fbc/stockSearch"  # wfs

# 平台仓发货单
mp_wh_shipment_url = "https://gw.lingxingerp.com/mp-platform-warehouse-api/api/shippingList/list"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Referer": "https://erp.lingxing.com/",
    "X-AK-Company-Id": "901140007506993664",
    "X-AK-ENV-KEY": "SAAS-94",
    "X-AK-PLATFORM": "1",
    "X-AK-Request-Id": "df5d3bc7-6901-4af0-b6e2-cfd06d37f34a",
    "X-AK-Request-Source": "erp",
    "X-AK-Version": "3.1.6.3.1.048",
    "X-AK-Zid": "200480"
}

