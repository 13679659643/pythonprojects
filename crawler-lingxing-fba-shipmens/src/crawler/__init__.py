# _*_ coding: utf-8 _*_
# @Time : 2024/8/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-fba-shipmens
# @Desc :
from digiCore.db.redis.core import RedisDao
from digiCore.db.tidb.core import TiDBDao
from digiCore.lingxing.crawler_http import RequestHelper


class CrawlerBase:

    def __init__(self):
        self.tidb_ob = TiDBDao()
        self.redis_ob = RedisDao()
        self.lx_api = RequestHelper()