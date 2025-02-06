# _*_ coding: utf-8 _*_
# @Time : 2023/7/11
# @Author : 张致富
# @Email ： zzf@doocn.com
# @File : crawler-lingxing-customer-data
# @Desc :

PROJECT_NAME = "crawler-lingxing-customer-data"
# 补全项目名称(一定要写)
PROJECT_TITLE = "爬虫获取领星客服板块数据"
# 接口路由
PROJECT_ROUTE = f"/api/v1/{PROJECT_NAME}/schedule"

# 数据服务告警通知
webhook = "https://oapi.dingtalk.com/robot/send?access_token=8b5c9d608f68b168e8d86b49a1efcb888703dc1a9ca24c754c2810fd00d7e95b"

# 子服务
fba_shipment_details_subserver = "crawler_customer_review_data"  # 爬取评论客服

# 领星客服评论数据
URL_REVIEW_API = 'https://erp.lingxing.com/api/customer_service/showReview'

# MongoDB
mongo_field_list = ['review_id']
db_name, table_name = "ods_crawler_lingxing", "ods_lingxing_customer_review_d"
