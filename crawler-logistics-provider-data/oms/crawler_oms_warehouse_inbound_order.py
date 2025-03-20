# -*- coding: utf-8 -*-
# @Time    : 2025/1/23 9:44
# @Author  : Night
# @File    : crawler_oms_warehouse_inbound_order.py
# @Description:
import copy
import json
from datetime import datetime, timedelta
import requests
from loguru import logger
from crawler_base import BaseCrawler
from db_model import ods_scg_wld_oms_warehouse_inbound_order_table, \
    ods_scg_wld_oms_warehouse_inbound_order_i_d_field_list
from settings import fetcher_info


class CrawlerOmsWarehouseInboundOrder(BaseCrawler):
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

    def etl_data(self, dataList):
        for data in dataList:
            data['dt'] = data['orderCreateTime'].split(" ")[0].replace("-", "")
            data['billItems'] = json.dumps(data['billItems'])
            for product in data['productList']:
                data_copy = copy.deepcopy(data)
                data_copy['sku'] = product['sku']
                data_copy['quantity'] = product['quantity']
                self.data_list.append(data_copy)

    def get_inbound_order(self, current: int = 1):
        """
        获取一件代发出库数据
        :return:
        """
        params = {
            'current': current,
            'size': '20',
            'whCodeList': '',
            'inboundType': '',
            'arrivalModeStr': '',
            'timeType': 'orderCreateTime',
            'orderType': 'inboundOrderNo',
            'barcodeType': 'sku',
            'barcode': '',
            'appendixFlag': '',
            'startTime': f'{self.start_date} 00:00:00',
            'endTime': f'{self.end_date} 23:59:59',
        }

        response = self.session.get('https://oms.xlwms.com/gateway/woms/inboundOrder/list', params=params)
        if response.status_code == 200:
            return response.json()
        return None

    def fetch_all_pages(self):
        """
        获取所有页面的数据
        """
        pageNo = 1
        while True:
            ret_data = self.get_inbound_order(pageNo)
            if not ret_data:
                break
            dataList = ret_data['data']['records']
            total = ret_data['data']['total']
            page_total_ct = (total - 1) // 20 + 1
            self.etl_data(dataList)
            if pageNo >= page_total_ct:
                break
            pageNo += 1

    def login(self):
        with self.redis_client.conn as redis_conn:
            if not redis_conn.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                data = {
                    'loginAccount': self.config[self.logistics_provider_code]['username'],
                    'password': self.config[self.logistics_provider_code]['password'],
                    'businessType': 'oms',
                }

                response = self.session.post('https://oms.xlwms.com/gateway/woms/auth/login', json=data)
                if response.json()['msg'] == '操作成功':
                    token = response.json()['data']['token']
                    redis_conn.hset(self.HASH_AUTH_TOKEN, self.key, token)
                    redis_conn.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 2 * 60 * 60, "1")
                    logger.info("澳得亚海外仓-登录账号成功")
                else:
                    logger.warning(f"登录请求失败，状态码：{response.status_code}")

            return redis_conn.hget(self.HASH_AUTH_TOKEN, self.key)

    def init_headers(self, token):
        """
        :param token:
        :return:
        """
        token_str = token.decode()
        self.session.headers['authorization'] = 'Bearer ' + token_str

    def insert_to_tidb(self):
        """
        存入到数据库中
        :return:
        """
        self.tidb.insert_data(ods_scg_wld_oms_warehouse_inbound_order_table,
                              ods_scg_wld_oms_warehouse_inbound_order_i_d_field_list,
                              self.data_list)
        logger.info(f'澳得亚海外仓-入库-数据同步{len(self.data_list)}完成')

    def main(self):
        self.init_logistic('OMS')
        token = self.login()
        if not token:
            return
        self.init_headers(token)
        self.fetch_all_pages()
        self.insert_to_tidb()


if __name__ == '__main__':
    CrawlerOmsWarehouseInboundOrder().main()
