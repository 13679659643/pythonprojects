# -*- coding: utf-8 -*-
# @Time    : 2025/1/9 10:15
# @Author  : Night
# @File    : crawler_kulu_inbound_warehouse_management.py
# @Description:
import base64
import json
from datetime import datetime, timedelta
import requests
from loguru import logger
from crawler_base import BaseCrawler
from db_model import ods_scg_wld_kulu_inbound_warehouse_management_table, \
    ods_scg_wld_kulu_inbound_warehouse_management_i_d_field_list
from settings import fetcher_info


class KuluInboundWarehouseManagement(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.session = requests.session()
        self.now_date = datetime.now()
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.start_date = (self.now_date - timedelta(days=90)).strftime('%Y-%m-%d')
        self.data_list = []

    def init_logistic(self, logistics_provider: str):
        self.logistics_provider = fetcher_info[logistics_provider]['logistics_provider']
        self.logistics_provider_code = logistics_provider
        self.HASH_AUTH_TOKEN = fetcher_info[logistics_provider]['hash_token_path']
        self.key = fetcher_info[logistics_provider]['token_key']

    def btoa(self,s: str) -> str:
        # 将字符串编码为字节
        byte_data = s.encode('utf-8')
        # 使用base64进行编码
        base64_encoded_data = base64.b64encode(byte_data)
        # 将结果解码回字符串形式并返回
        return base64_encoded_data.decode('utf-8')

    def get_receiving_data(self, page: int = 1):
        """
        :param page: 页数
        :return:
        """
        data = {
            'time-type': 'receiving_add_time',
            'order-type': 'DESC',
            'common_code': '',
            'Sku': '',
            'E1': '',
            'E2': '',
            'E10': '',
            'E3': '',
            'E35': '',
            'customer_type': '',
            'transit_type': '',
            'income_type': '',
            'asn_type': '',
            'create_original': '',
            'tracking_number': '',
            'box_no': '',
            'dateType': '1',
            'dateFor': '',
            'dateTo': '',
        }

        response = self.session.post(
            f'http://kulu.yunwms.com/receiving/receiving/list/page/{page}/pageSize/20',
            data=data,
            verify=False,
        )
        if response.status_code == 200:
            return response.json()
        return None

    def etl_data(self, dataList):
        """
        列表数据
        :param dataList:
        :return:
        """
        for row in dataList:
            row['dt'] = row['receiving_add_time'].split(" ")[0].replace("-", "")
            row['putaway_qty']=row['detail_qty']['putaway_qty']
            row['received_qty'] = row['detail_qty']['received_qty']
            row['receiving_qty'] = row['detail_qty']['receiving_qty']
            row['transfer_qty'] = row['detail_qty']['transfer_qty']
            self.data_list.append(row)

    def fetch_all_pages(self):
        """
        获取所有页面的数据
        """
        pageNo = 1
        while True:
            ret_data = self.get_receiving_data(pageNo)
            if not ret_data:
                break
            dataList = ret_data['data']
            total = int(ret_data['total'])
            page_total_ct = (total - 1) // 20 + 1
            self.etl_data(dataList)
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
        self.tidb.insert_data(ods_scg_wld_kulu_inbound_warehouse_management_table,
                              ods_scg_wld_kulu_inbound_warehouse_management_i_d_field_list,
                              self.data_list)
        logger.info(f'酷麓海外仓-入库单管理数据同步{len(self.data_list)}完成')

    def main(self):
        self.init_logistic('KULU')
        kl_cookie=self.login()
        if not kl_cookie:
            return
        self.init_headers(kl_cookie)
        self.fetch_all_pages()
        self.insert_to_tidb()


if __name__ == '__main__':
    kulu = KuluInboundWarehouseManagement()
    kulu.main()
