# -*- coding: utf-8 -*-
# @Time    : 2025/1/23 9:07
# @Author  : Night
# @File    : crawler_kulu_inbound_warehouse_management_detail.py
# @Description:
import base64
import json
from datetime import datetime, timedelta
import requests
from loguru import logger
from crawler_base import BaseCrawler
from db_model import ods_scg_wld_kulu_inbound_warehouse_management_detail_table, \
    ods_scg_wld_kulu_inbound_warehouse_management_detail_i_d_field_list
from settings import fetcher_info


class KuluInboundWarehouseManagementDetail(BaseCrawler):
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

    def btoa(self, s: str) -> str:
        # 将字符串编码为字节
        byte_data = s.encode('utf-8')
        # 使用base64进行编码
        base64_encoded_data = base64.b64encode(byte_data)
        # 将结果解码回字符串形式并返回
        return base64_encoded_data.decode('utf-8')

    def get_view_detail_product(self, code: str, page: int = 1):
        """
        :param page: 页数
        :return:
        """
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://kulu.yunwms.com',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = {
            'code': code,
        }

        response = self.session.post(
            f'http://kulu.yunwms.com/receiving/receiving/view-detail-by-product/page/{page}/pageSize/20',
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
            row['dt'] = row['rd_update_time'].split(" ")[0].replace("-", "")  # 更新时间
            self.data_list.append(row)

    def get_inbound_id(self):
        sql = f"SELECT receiving_code FROM ods_prod.ods_scg_wld_kulu_inbound_warehouse_management_i_d where dt>='{self.start_date.replace('-', '')}' and dt<='{self.end_date.replace('-', '')}'"
        inbound_ids = self.tidb.query_list(sql)
        return [i['receiving_code'] for i in inbound_ids]

    def fetch_all_pages(self):
        """
        获取所有页面的数据
        """
        inbound_ids = self.get_inbound_id()
        for id in inbound_ids:
            pageNo = 1
            while True:
                ret_data = self.get_view_detail_product(id, pageNo)
                if not ret_data:
                    break
                total = int(ret_data['total'])
                page_total_ct = (total - 1) // 20 + 1
                dataList = ret_data['data']
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
        self.tidb.insert_data(ods_scg_wld_kulu_inbound_warehouse_management_detail_table,
                              ods_scg_wld_kulu_inbound_warehouse_management_detail_i_d_field_list,
                              self.data_list)
        logger.info(f'酷麓海外仓-入库单管理详情数据同步{len(self.data_list)}完成')

    def main(self):
        self.init_logistic('KULU')
        kl_cookie = self.login()
        if not kl_cookie:
            return
        self.init_headers(kl_cookie)
        self.fetch_all_pages()
        self.insert_to_tidb()


if __name__ == '__main__':
    kulu = KuluInboundWarehouseManagementDetail()
    kulu.main()
