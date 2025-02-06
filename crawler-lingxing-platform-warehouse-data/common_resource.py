# _*_ coding: utf-8 _*_
# @Time : 2024/3/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-data-quality-monitor
# @Desc : 基类
import requests
from digiCore.db_init import InstantiationDB


class Base:

    def __init__(self):
        self.idb = InstantiationDB()
        self.tidb_ob = self.idb.load_tidb_ob()
        self.redis_ob = self.idb.load_redis_ob()
        self.mongo_ob = self.idb.load_mongodb_ob()
        self.headers = {}

    def init_headers(self):
        """
        获取钉钉的access_token
        :return:
        """
        _access_token = self.redis_ob.get_lingxing_crawler_auth_token()
        self.headers = {
            "X-AK-Company-Id": "901140007506993664",
            "auth-token": f"{_access_token}"
        }

        return self.headers

    def post(self, url, data):
        headers = self.init_headers()
        response = requests.post(url=url, json=data, headers=headers).json()
        code = response.get("code")
        if int(code) != 1:
            return {}
        return response

    def get(self,url):
        headers = self.init_headers()
        response = requests.get(url=url, headers=headers).json()
        code = response.get("code")
        if int(code) != 1:
            return {}
        return response

if __name__ == '__main__':
    b = Base()
