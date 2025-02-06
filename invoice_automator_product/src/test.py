import requests

# tt = 'http://192.168.0.201:8120/api/v1/invoice_automator_product/schedule/fba'
# url = 'http://127.0.0.1:8000/api/v1/invoice_automator_product/schedule/fba'
# params1 = {
#     'shipment_id': 'FBA18GWJVGNT',
#     'amz_code': '5P9YBCHJ'
# }
# params2 = {
#     'shipment_id': 'FBA18H3N3461',
#     'amz_code': '1955EC4E'
# }
# params3 = {
#     'shipment_id': 'FBA15JD0Y2GR',
#     'amz_code': '2SQDDFJQ'
# }
# data_list = [#params1,
#              #params2,qe
#              params3
#              ]
# for param in data_list:
#     response = requests.get(url, params=param)
#     print(response.json())
url = 'http://110.191.179.224:8604/api/v1/logistics-provider-info-sync/schedule/syna_local_shipment_weight_data'
response = requests.get(url)
print(response.text)
