# -*- coding: utf-8 -*-
# @Time    : 2024/07/25
# @Author  : night
# @Email   :
# @File    :
# @Software: 基础信息配置
from digiCore.db_init import InstantiationDB
from digiCore.send_to_group import SendToGroup
from settings import webhook


class BaseCrawler:
    def __init__(self):
        self.idb = InstantiationDB()
        self.redis_ob = self.idb.load_redis_ob()
        self.tidb_ob = self.idb.load_tidb_ob()
        self.mongo_ob = self.idb.load_mongodb_ob()
        self.dd_ob = SendToGroup(webhook)

    def get_available_headers(self):
        """
        获取可用handers头
        :param headers: 请求头
        :return:
        """
        auth_token = self.redis_ob.get_lingxing_crawler_auth_token()
        headers = {
            "X-AK-Company-Id": "901140007506993664",
            "auth-token": auth_token
        }
        return headers

    def main(self):
        pass


if __name__ == '__main__':
    cl = BaseCrawler()
    cl.main()
