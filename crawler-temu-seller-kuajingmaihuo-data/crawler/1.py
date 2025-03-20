# -*- coding: utf-8 -*-
# @Time    : 2025/3/14 9:17
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import datetime

from base.crawler_base import CrawlerBase
#
# timestamp1 = 1741888273888 / 1000.0
# timestamp2 = 1741449600000 / 1000.0
#
# date1 = CrawlerBase().timestr(1741888273888)
# date11 = datetime.datetime.fromtimestamp(timestamp1)
# date2 = datetime.datetime.fromtimestamp(timestamp2)
#
# print(date1)
# print(date11)
# print(date2)
# exit()

import requests

cookies = {
    'api_uid': 'Cp13kmduaTJ0RQBAcuf/Ag==',
    '_bee': 'x4I7rions1tAxxkV81qRcmfJKKTgPapr',
    'njrpl': 'x4I7rions1tAxxkV81qRcmfJKKTgPapr',
    'dilx': 'Z9u45EO7eVShaHa1VWo5U',
    'hfsc': 'L3yJfYs44Djw057FeA==',
    '_nano_fp': 'XpmYXpPxn598XqdoXC_Saa9rwEELlHwfb6RMFxhk',
    'timezone': 'Asia%2FShanghai',
    'webp': '1',
    'region': '0',
    'mallid': '634418216187136',
    'seller_temp': 'N_eyJ0IjoiWHlCY2ttdUc1TnRjS0FVVE8vUy9PWDN6RTI0Um1zMTF6OGR2SksxZVFXNW1acVNickl2ZXBQMEgvUWNnUXRhaERHeHNZbU9tRVRiZEpDeGhHcXdocmc9PSIsInYiOjEsInMiOjEwMDAxLCJ1IjoyMTkzNzMxNjMzMzA5NH0=',
}

headers = {
    'authority': 'agentseller-us.temu.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json;charset=UTF-8',
    # 'cookie': 'api_uid=Cp13kmduaTJ0RQBAcuf/Ag==; _bee=x4I7rions1tAxxkV81qRcmfJKKTgPapr; njrpl=x4I7rions1tAxxkV81qRcmfJKKTgPapr; dilx=Z9u45EO7eVShaHa1VWo5U; hfsc=L3yJfYs44Djw057FeA==; _nano_fp=XpmYXpPxn598XqdoXC_Saa9rwEELlHwfb6RMFxhk; timezone=Asia%2FShanghai; webp=1; region=0; mallid=634418216187136; seller_temp=N_eyJ0IjoiWHlCY2ttdUc1TnRjS0FVVE8vUy9PWDN6RTI0Um1zMTF6OGR2SksxZVFXNW1acVNickl2ZXBQMEgvUWNnUXRhaERHeHNZbU9tRVRiZEpDeGhHcXdocmc9PSIsInYiOjEsInMiOjEwMDAxLCJ1IjoyMTkzNzMxNjMzMzA5NH0=',
    'mallid': '634418216187136',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

json_data = {
    'parentOrderSn': 'PO-211-09300567122473045',
    'parentAfterSalesSn': 'PO-211-09300567122473045-D01',
    # 'cprSn': 'CPR-211-3045-5781282',
}

response = requests.post(
    'https://agentseller-us.temu.com/garen/mms/afterSales/queryReturnDetails',
    cookies=cookies,
    headers=headers,
    json=json_data,
)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"parentOrderSn":"PO-211-09300567122473045","parentAfterSalesSn":"PO-211-09300567122473045-D01","cprSn":"CPR-211-3045-5781282"}'
#response = requests.post(
#    'https://agentseller-us.temu.com/garen/mms/afterSales/queryReturnDetails',
#    cookies=cookies,
#    headers=headers,
#    data=data,
#)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"parentOrderSn":"PO-211-09300567122473045","parentAfterSalesSn":"PO-211-09300567122473045-D01","cprSn":"CPR-211-3045-5781282"}'
#response = requests.post(
#    'https://agentseller-us.temu.com/garen/mms/afterSales/queryReturnDetails',
#    cookies=cookies,
#    headers=headers,
#    data=data,
#)
print(response.json())