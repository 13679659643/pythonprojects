# -*- coding: utf-8 -*-
# @Time    : 2024/12/10 16:20
# @Author  : Night
# @File    : crawler_base.py
# @Description:
import json
import time
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector


class CrawlerBase:
    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.cookies = {}

    def init_user_cookies(self, db_key, account):
        """
        获取 平台对应 各个账号cookies
        :param db_key: redis账号键
        :param account: 账号
        """
        redis_key = f"{db_key}:{account}"
        auth_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not auth_cookie:
            return
        try:
            # 尝试解析JSON字符串
            cookie_dict = json.loads(auth_cookie) if isinstance(auth_cookie, str) else auth_cookie
        except json.JSONDecodeError:
            # 如果解析失败，则认为它不是一个有效的JSON字符串
            cookie_dict = auth_cookie
        self.cookies = cookie_dict

    def generate_date_list(self, in_day: int = 7):
        """
        :param in_day: 天数
        :return:
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=in_day)

        # 创建日期列表
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        return dates

    def get_time_range(self, in_day: int = 30):
        """
        获取一段时间范围内
        """
        end_date_sft = datetime.now()
        start_date = (end_date_sft - timedelta(days=in_day)).strftime('%Y-%m-%d')
        end_date = end_date_sft.strftime('%Y-%m-%d')
        return start_date, end_date

    def save_to_tidb(self, db_table, field_list, data_list):
        """
        :param db_table: 表名
        :param field_list: 字段列表
        :param data_list: 列表数据
        :return:
        """
        self.tidb.insert_data(db_table, field_list,
                              data_list)

    def main(self):
        pass


class RetryDecorator:
    @classmethod
    def retry_decorator(cls, msg=None, error_type=None, max_retry_count: int = 5, time_interval: int = 2):
        """
        任务重试装饰器
        msg:错误信息
        error_type：错误类型
        max_retry_count: 最大重试次数 默认5次
        time_interval: 每次重试间隔 默认2s
        @RetryDecorator.retry_decorator(msg="存放错误信息的位置", error_type=713, max_retry_count=3, time_interval=1)
        def my_function():
            a = 1
            b = json.loads(a)
            print(b)
            print(type(b))
            return b
        """

        def _retry(func):
            # 保留原始函数的元数据（如函数名、文档字符串、参数列表等）
            @wraps(func)
            def wrapper(*args, **kwargs):
                for retry_count in range(max_retry_count):
                    try:
                        """
                        *args 和 **kwargs 是 Python 中的惯例写法，用于处理函数定义中的可变数量的位置参数和关键字参数:
                        *args：这个写法表示接受任意数量的位置参数，并将它们作为一个元组传递给函数。在函数内部，可以通过 args 这个元组来访问这些位置参数。
                        **kwargs：这个写法表示接受任意数量的关键字参数，将它们作为一个字典传递给函数。在函数内部，可以通过 kwargs 这个字典来访问这些关键字参数。
                        """
                        task_result = func(*args, **kwargs)
                        return task_result

                    except Exception as e:
                        logger.error(msg if msg else f"{max_retry_count}： 函数报错，正在重试！")
                        time.sleep(time_interval)
                # 如果超过最大重试次数仍未成功,则返回指定的错误类型或默认值.
                return logger.error(error_type) if error_type else f"超过最大重试次数仍未成功！"

            # 装饰器的必要结构：返回了包装原始函数的函数,实现了在函数执行前后添加额外逻辑的功能.
            return wrapper

        # 返回了装饰器函数,使得外部可以通过 @Decorate.def_retry() 的方式来调用这个装饰器.
        return _retry


if __name__ == '__main__':
    base = CrawlerBase()
    base.main()
