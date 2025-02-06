# -*- coding: utf-8 -*-
# @Time    : 2024/12/17 14:27
# @Author  : Night
# @File    : crawler-vis-product-operation-inventory.py
# @Description:
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from loguru import logger
from base.crawler_base import CrawlerBase, RetryDecorator
from settings import RedisKeys
from vis.db_model import ods_cd_sl_vis_product_operation_inventory_i_d_db_table, \
    ods_cd_sl_vis_product_operation_inventory_i_d_field_list


class CrawlerVisProductOperationInventory(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def get_account(self, db_key, account):
        redis_key = f"{db_key}:{account}:*"
        stores = self.redis_client.client.keys(redis_key)
        return stores

    def init_user_cookies(self, redis_key, account=''):
        """
        获取 平台对应 各个账号cookies
        :param db_key: redis账号键
        """
        auth_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not auth_cookie:
            return
        if not isinstance(auth_cookie, str):
            cookie_dict = auth_cookie
        else:
            cookie_dict = json.loads(auth_cookie)
        self.cookies = cookie_dict

    def etl_data(self, store: str, good_list: list):
        data_list = []
        for good in good_list:
            good['store'] = store[store.rindex(':') + 1:]
            data_list.append(good)
        return data_list

    RetryDecorator.retry_decorator()

    def get_good_list(self, pageNo, s_date):
        """l
        :param pageNo 页数
        :param s_date 日期
        """
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://compass.vip.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://compass.vip.com/frontend/index.html',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        date_time_sft = s_date.replace("-", "")
        json_data = {
            'brandStoreSn': 'all',
            'dtType': 0,
            'calType': 1,
            'startDt': date_time_sft,
            'endDt': date_time_sft,
            'queryHll': False,
            'pageNo': pageNo,
            'pageSize': 50,
            'dimType': 1,
            'channelType': 1,
        }
        response = requests.post('https://compass.vip.com/product/detail/getGoodsList', cookies=self.cookies,
                                 headers=headers, json=json_data, timeout=15)
        if response.status_code != 200:
            logger.info(f'唯品会-货品运营-商品明细 {date_time_sft} 采集失败')
            return
        ret_data = response.json()['data']
        if not ret_data:
            return
        return ret_data

    def fetch_all_pages(self, store, sdate):
        """
        获取所有页面的数据
        """
        pageNo = 1
        data_list = []
        while True:
            ret_data = self.get_good_list(pageNo, sdate)
            if not ret_data:
                break
            goodsList = ret_data['goodsList']
            total = ret_data['total']
            page_total_ct = (total - 1) // 50 + 1
            good_list = self.etl_data(store, goodsList)
            data_list.extend(good_list)
            if pageNo >= page_total_ct:
                break
            pageNo += 1
        return data_list

    def process_store(self, key, sdate):
        self.init_user_cookies(key)
        data_list = self.fetch_all_pages(key, sdate)
        store_name = key.split(':')[-1]
        with self.lock:
            self.save_to_tidb(ods_cd_sl_vis_product_operation_inventory_i_d_db_table,
                              ods_cd_sl_vis_product_operation_inventory_i_d_field_list, data_list)
            logger.info(f'唯品会-货品运营-商品明细 {store_name} {len(data_list)} {sdate}采集完成')

    def main(self):
        user_infos = self.tidb.get_user_info('VIS')
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for dw_info in user_infos:
                account = dw_info['account']
                stores = self.get_account(RedisKeys.VIS_VIP_LOGIN_KEY.value, account)
                for store in stores:
                    key = store.decode()
                    for sdate in self.generate_date_list(in_day=40):
                        futures.append(executor.submit(self.process_store, key, sdate))
                    for future in as_completed(futures):
                        future.result()


if __name__ == "__main__":
    vis = CrawlerVisProductOperationInventory()
    vis.main()
