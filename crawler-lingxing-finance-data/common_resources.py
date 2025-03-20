# _*_ coding: utf-8 _*_
# @Time : 2024/3/15
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-finance-data
# @Desc : 基类
import time

import requests
from digiCore import Decorate
from digiCore.db_init import InstantiationDB


class CrawlerBase:
    def __init__(self):
        self.idb = InstantiationDB()
        self.redis_ob = self.idb.load_redis_ob()
        self.tidb_ob = self.idb.load_tidb_ob()
        self.headers = {}
        self.extra_params = {}

    def init_headers(self):
        if self.headers:
            return self.headers
        headers = {
            'x-ak-company-id': '901140007506993664',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        auth_token = self.redis_ob.get_lingxing_crawler_auth_token()
        headers['auth-token'] = auth_token
        self.headers = headers
        return headers

    def init_task(self, *args):
        return

    @Decorate.def_retry(msg='请求失败，正在重试！')
    def post(self, url, data):
        """
        请求获取页面数据
        """
        _headers = self.init_headers()
        response = requests.post(url, json=data, headers=_headers)
        if response.status_code != 200:
            return {}
        return response.json()

    def consume_task(self, task):
        """
        通过判断是否存在下一页来结束请求
        """
        pass

    def format_data(self, records, task):
        """
        格式化数据为可保存到数据库的数据
        """
        pass

    def original_to_format_key(self, order_data_list: list, table_dict: dict):
        """
        将读取出来的原始数据的key更换为格式化之后的key，并去多余key。
        :return:
        """
        new_data_list = []
        for data in order_data_list:
            # 找出原始数据中不存在的字段
            diff_keys = set(table_dict.keys()) - set(data.keys())
            new_item = {table_dict.get(k, k): str(v) for k, v in
                        data.items()
                        if k in table_dict}
            # 对不存在的字段进行赋值
            for key in diff_keys:
                if key == "dt":
                    continue
                new_item[table_dict[key]] = "None"
            new_data_list.append(new_item)
        return new_data_list