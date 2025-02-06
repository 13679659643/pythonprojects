# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:


import redis
import configparser
import os



class RedisClient:
    def __init__(self, host='192.168.0.201', port=6379, db=0, password=None):
        self.client = redis.Redis(host=host, port=port, db=db, password=password)


    def redis_client(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../', 'conf', 'config.ini')
        config.read(config_path, encoding='utf-8')
        redis_password = config['redis']['password']
        self.client = RedisClient(host='192.168.0.201', port=16379, db=5, password=redis_password)
        return self.client

    def set_auth_cookie(self, redis_key, cookie_str: str = ''):
        """
        设置cookie_str
        将 cookie_str 设置为 redis_key 的值，并设置一个过期时间（单位为秒）
        """
        self.client.setex(redis_key, 60 * 60 * 24 * 5, cookie_str)

    def get_auth_cookie(self, key_name):
        """
        获取cookie_str，decode_responses=True 参数的作用是将从 Redis 返回的字节数据自动解码为 Python 字符串。
        默认情况下，Redis 返回的数据是字节类型（bytes），如果设置了 decode_responses=True，则返回的数据会被解码为字符串（str）
        :param key_name:
        :return:获取 key_name 的值，并使用 decode 方法将值从字节串转换为字符串。
        """
        value = self.client.get(key_name)
        if value is None:
            return ''  # 或者你可以返回一个默认值，或者抛出一个异常
        else:
            return self.client.get(key_name).decode()
            # return value.decode()
        # return self.client.get(key_name).decode()


if __name__ == "__main__":
    redis_client = RedisClient()
