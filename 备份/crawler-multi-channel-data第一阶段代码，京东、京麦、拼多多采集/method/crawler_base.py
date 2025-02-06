# -*- coding: utf-8 -*-
# @Time    : 2024/12/16 10:58
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    : 
# @Software:
import subprocess
from functools import wraps

from loguru import logger
import json
from datetime import datetime, timedelta
import random
import time
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from pdd import get_file_path
from settings import RedisKeys


class BaseCrawler:
    def __init__(self):
        self.redis_client = RedisClient().redis_client()

    def get_cookies(self, account: str):
        redis_key = f"{RedisKeys.PDD_MMS_LOGIN_KEY.value}:{account}"
        pdd_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not pdd_cookie:
            logger.info(f"拼多多 {account} cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        pdd_cookie_dict = json.loads(pdd_cookie)
        return pdd_cookie_dict

    @staticmethod
    def generate_date_list():
        # 获取当前日期和七天前的日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # # 将字符串转化为日期
        # start_date = datetime.strptime('2024-12-01', '%Y-%m-%d')
        # end_date = datetime.strptime('2024-12-17', '%Y-%m-%d')
        # 创建日期列表
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        return dates

    @staticmethod
    def get_anti_content():
        """
        加密生成anti-content
        :return:
        """
        _ = subprocess.run(["node", get_file_path("../pdd/home_detail_content.js")], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           universal_newlines=True)
        anti_content = _.stdout.strip()
        return anti_content

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
                        format_error_msg(e)
                        time.sleep(time_interval)
                # 如果超过最大重试次数仍未成功,则返回指定的错误类型或默认值.
                return logger.error(error_type) if error_type else f"超过最大重试次数仍未成功！"

            # 装饰器的必要结构：返回了包装原始函数的函数,实现了在函数执行前后添加额外逻辑的功能.
            return wrapper

        # 返回了装饰器函数,使得外部可以通过 @Decorate.def_retry() 的方式来调用这个装饰器.
        return _retry


def format_error_msg(e):
    """
    日志输出所在的文件路径、行号、具体错误信息。
    :param e:
    :return:
    """
    # 这一行代码获取了错误发生时所在的文件名,并使用 logger.error() 方法将其记录到日志中.
    logger.error(f'错误文件路径:{e.__traceback__.tb_frame.f_globals["__file__"]}')
    # 获取错误所在的行号.
    logger.error(f'代码错误行位置:{e.__traceback__.tb_lineno}')
    # 这一行代码获取了错误的消息内容,并使用 logger.error() 方法将其记录到日志中.e.args 通常包含了错误的具体信息或描述.
    logger.error(f'错误信息:{e.args}')



if __name__ == "__main__":
    bc = BaseCrawler()
    bc.main()