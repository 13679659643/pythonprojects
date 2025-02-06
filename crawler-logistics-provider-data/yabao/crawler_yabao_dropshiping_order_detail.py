# -*- coding: utf-8 -*-
# @Time    : 2025/1/15 14:31
# @Author  : Night
# @File    : crawler_yabao_dropshiping_order_detail.py
# @Description:
import json
from datetime import datetime, timedelta
import requests
from loguru import logger
from crawler_base import BaseCrawler
from db_model import ods_scg_wld_yabao_dropshipping_order_detail_table, \
    ods_scg_wld_yabao_dropshipping_order_detail_i_d_field_list
from settings import fetcher_info


class CrawlerYapaoOverseasWarehouse(BaseCrawler):
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

    def get_order_detail(self, order_id: str):
        """
        :param page: 页数
        :return:
        """
        params = {
            'OrderMainID': order_id,
            'page': '1',
            'limit': '10',
        }

        response = self.session.get(
            'http://47.106.234.129:808/Home/GetGoodsInfo',
            params=params,
            verify=False,
        )
        if response.status_code == 200:
            return response.json()
        return None

    def etl_data(self, dataList, id):
        """
        列表数据
        :param dataList:
        :return:
        """
        for row in dataList:
            row['OrderMainID'] = id
            self.data_list.append(row)

    def fetch_all_pages(self):
        """
        获取所有页面的数据
        """
        order_ids = self.get_order_id()
        for id in order_ids:
            ret_data = self.get_order_detail(id)
            if not ret_data:
                break
            dataList = ret_data['data']
            self.etl_data(dataList, id)

    def init_headers(self):
        """
        更新账号登录cookie
        :return:
        """
        with self.redis_client.conn as redis_conn:
            cookies = redis_conn.hget(self.HASH_AUTH_TOKEN, self.key)
            cookie_dict = json.loads(cookies.decode())
            self.session.cookies.update(cookie_dict)

    def get_order_id(self):
        sql = f"SELECT OrderMainID FROM ods_prod.ods_scg_wld_yabao_dropshipping_order_i_d where dt>='{self.start_date.replace('-', '')}' and dt<='{self.end_date.replace('-', '')}'"
        order_ids = self.tidb.query_list(sql)
        return [i['OrderMainID'] for i in order_ids]

    def insert_to_tidb(self):
        """
        存入到数据库中
        :return:
        """
        self.tidb.insert_data(ods_scg_wld_yabao_dropshipping_order_detail_table,
                              ods_scg_wld_yabao_dropshipping_order_detail_i_d_field_list,
                              self.data_list)
        logger.info(f'亚豹海外仓-出库详情数据同步{len(self.data_list)}完成')

    def main(self):
        self.init_logistic('YABAO')
        self.init_headers()
        self.fetch_all_pages()
        self.insert_to_tidb()


if __name__ == '__main__':
    CrawlerYapaoOverseasWarehouse().main()
