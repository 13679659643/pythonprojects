import requests

# 测试 GET 路由
# response = requests.get('http://127.0.0.1:8000/api/v1/crawler-logistics-provider-data/schedule')
# print(response.json())

# 启动异步任务的 POST 路由
# post_data = {
#     "service_name": "crawler-logistics-provider-data",
#     "subserver": "LogisticsDataFetcher_nextsls",
#     "operation_type": "async",
#     "run_sign": "start",
#     "extra_params": {}
# }
# response = requests.post('http://127.0.0.1:8000/api/v1/crawler-logistics-provider-data/schedule', json=post_data)
# print(response.json())


# post_data = {
#     "service_name": "crawler-logistics-provider-data",
#     "subserver": "LogisticsDataFetcher_tw",
#     "operation_type": "async",
#     "run_sign": "start",
#     "extra_params": {}
# }
# response = requests.post('http://127.0.0.1:8000/api/v1/crawler-logistics-provider-data/schedule', json=post_data)
# print(response.json())


