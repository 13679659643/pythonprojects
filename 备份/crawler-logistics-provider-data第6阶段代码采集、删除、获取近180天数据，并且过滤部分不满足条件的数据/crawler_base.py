# -*- coding: utf-8 -*-
# @Time    : 2024/9/5 10:42
# @Author  : Night
# @File    : crawler_base.py
# @Description:
from datetime import datetime, timedelta

from digiCore.db.tidb.core import TiDBDao
from digiCore.db.redis.core import RedisDao
import requests
import redis
import configparser

from loguru import logger

from settings import fetcher_info
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, './config.ini')


class BaseCrawler:
    def __init__(self):
        self.session = None
        self.tidb = TiDBDao('192.168.0.200')
        self.redis_client = RedisDao()
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')
        self.logistics_provider = None
        self.logistics_provider_code = None
        self.HASH_AUTH_TOKEN = None
        self.key = None
        self.token_url = None
        self.data_url = None
        self.view_url = None
        self.db_table = None
        self.create_table_query = None
        self.truncate_table_query = None
        self.table_field_list = None
        self.db_view = None
        self.create_view_query = None
        self.truncate_view_query = None
        self.view_field_list = None

    def init_logistic(self, logistics_provider: str):
        """初始化物流商、token键值路径、网页url、数据库列表、名字、创建语句"""
        self.logistics_provider = fetcher_info[logistics_provider]['logistics_provider']
        self.logistics_provider_code = logistics_provider
        self.HASH_AUTH_TOKEN = fetcher_info[logistics_provider]['hash_token_path']
        self.key = fetcher_info[logistics_provider]['token_key']
        self.token_url = fetcher_info[logistics_provider]['get_token_url']
        self.data_url = fetcher_info[logistics_provider]['get_data_url']
        self.view_url = fetcher_info[logistics_provider]['view_url']
        self.db_table = fetcher_info[logistics_provider]['db_table']
        self.create_table_query = fetcher_info[logistics_provider]['create_table_query']
        self.truncate_table_query = fetcher_info[logistics_provider]['truncate_table_query']
        self.table_field_list = fetcher_info[logistics_provider]['table_field_list']
        self.db_view = fetcher_info[logistics_provider]['db_view']
        self.create_view_query = fetcher_info[logistics_provider]['create_view_query']
        self.truncate_view_query = fetcher_info[logistics_provider]['truncate_view_query']
        self.view_field_list = fetcher_info[logistics_provider]['view_field_list']

    def get_auth_token(self):
        """从 Redis 获取或请求新的认证 token，使用哈希存储多个键值对"""
        try:
            with self.redis_client as redis_client:
                if not redis_client.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                    json_data = {
                        'username': self.config[self.logistics_provider_code]['username'],
                        'password': self.config[self.logistics_provider_code]['password'],
                    }
                    response = self.session.post(self.token_url, json=json_data)
                    # 检查请求是否成功。如果请求返回的状态码不是 2xx，会抛出一个 HTTPError 异常：response.raise_for_status()
                    if response.status_code == 200:
                        token_data = response.json()['data']['token']
                        # 设置哈希存储键值对：将 token 存储到 Redis 中
                        redis_client.hset(self.HASH_AUTH_TOKEN, self.key, token_data)
                        # 使用单独的键存储过期时间：并设置过期时间为86400s即1天
                        redis_client.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 8 * 60 * 60, "1")
                        logger.info("token获取成功!")
                    else:
                        logger.warning(f"登录请求失败，状态码：{response.status_code}")
                        return None
                # 获取哈希字段的值：返回 Redis 中 名称为key的string的value
                return redis_client.hget(self.HASH_AUTH_TOKEN, self.key)
        # 处理 Redis 客户端在执行 Redis 操作时可能抛出的所有异常的基类
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            # 可以考虑在此处添加备用的 token 获取方式
            raise
        # 捕获网络请求相关的所有异常，包括连接错误、超时、重定向错误等
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            # 使用 raise 关键字重新引发捕获的异常,可以一直向上捕获
            raise

    def main(self):
        pass


if __name__ == "__main__":
    bc = BaseCrawler()
    bc.main()