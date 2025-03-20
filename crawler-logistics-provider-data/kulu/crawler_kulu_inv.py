# _*_ coding: utf-8 _*_
# @Time : 2025-02-27
# @Author : 李仕春
# @Email ： scli@doocn.com
# @File : crawler-logistics-provider-data
# @Desc : 采集kulu海外仓 库存
import base64
import copy
import json
from datetime import datetime, timedelta

import requests
from loguru import logger

from crawler_base import BaseCrawler
from db_model import ods_scg_wld_kulu_inv_management_table, ods_scg_wld_kulu_inv_management_list
from settings import fetcher_info


class CrawlerKuliInv(BaseCrawler):

        def __init__(self):
            super().__init__()
            self.session = requests.session()
            self.data_list = []

        def init_logistic(self, logistics_provider: str):
            self.logistics_provider = fetcher_info[logistics_provider]['logistics_provider']
            self.logistics_provider_code = logistics_provider
            self.HASH_AUTH_TOKEN = fetcher_info[logistics_provider]['hash_token_path']
            self.key = fetcher_info[logistics_provider]['token_key']

        def btoa(self, s: str) -> str:
            # 将字符串编码为字节
            byte_data = s.encode('utf-8')
            # 使用base64进行编码
            base64_encoded_data = base64.b64encode(byte_data)
            # 将结果解码回字符串形式并返回
            return base64_encoded_data.decode('utf-8')

        def get_inv_data(self, page: int = 1):
            """
            :param page: 页数
            :return:
            """
            data = {
    'order_by': '',
    'ac': '',
    'export_id': '',
    'export_type': '',
    'early_warning': '',
    'timing_hour': '',
    'timing_minute': '',
    'product_barcode_type': '',
    'product_barcode': '',
    'warehouse_id': '',
    'product_name': '',
    'item_ean': '',
    'reference_no': '',
    'qty_type': '',
    'qty_from': '',
    'qty_to': '',
    'morequery_field': '',
    'morequery_value': '',
}
            response = self.session.post(
                f'https://kulu.yunwms.com/product/inventory-wms/list/page/{page}/pageSize/200',
                data=data,
                verify=False,
            )
            if response.status_code == 200:
                return response.json()
            return None




        def fetch_all_pages(self):
            """
            获取所有页面的数据
            """
            pageNo = 1
            while True:
                ret_data = self.get_inv_data(pageNo)
                if not ret_data:
                    break
                detaList = ret_data['data']
                total = int(ret_data['total'])
                page_total_ct = (total - 1) // 200 + 1
                if not detaList:
                    break
                self.data_list += detaList
                if pageNo >= page_total_ct:
                    break
                pageNo += 1

        def login(self):
            with self.redis_client.conn as redis_conn:
                if not redis_conn.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                    data = {
                        'userName': self.config[self.logistics_provider_code]['username'],
                        'userPass': self.btoa(self.config[self.logistics_provider_code]['password']),
                    }

                    response = self.session.post('http://kulu.yunwms.com/default/index/login',
                                                 data=data, verify=False)
                    if response.json()['message'] == 'Success':
                        set_cookies = dict(response.cookies)
                        redis_conn.hset(self.HASH_AUTH_TOKEN, self.key, json.dumps(set_cookies))
                        redis_conn.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 2 * 60 * 60, "1")
                        logger.info("酷麓海外仓-登录账号成功")
                    else:
                        logger.warning(f"登录请求失败，状态码：{response.status_code}")

                return redis_conn.hget(self.HASH_AUTH_TOKEN, self.key)

        def init_headers(self, cookies):
            """
            更新账号登录cookie
            :param cookies:
            :return:
            """
            cookie_dict = json.loads(cookies.decode())
            self.session.cookies.update(cookie_dict)

        def insert_to_tidb(self):
            """
            存入到数据库中
            :return:
            """
            truncate_sql = "truncate table ods_prod.ods_scg_wld_kulu_inv_management_a_h;"
            self.tidb.commit_sql(truncate_sql)
            logger.info("清空全部数据")

            self.tidb.insert_data(ods_scg_wld_kulu_inv_management_table,
                                  ods_scg_wld_kulu_inv_management_list,
                                  self.data_list)
            logger.info(f'酷麓海外仓-库存管理数据同步{len(self.data_list)}完成')


        def main(self):
            self.init_logistic('KULU')
            kl_cookie = self.login()
            if not kl_cookie:
                return
            self.init_headers(kl_cookie)
            self.fetch_all_pages()
            self.insert_to_tidb()


if __name__ == '__main__':
    kulu = CrawlerKuliInv()
    kulu.main()

