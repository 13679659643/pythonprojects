# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:

import random
import subprocess
import time
from datetime import datetime, timedelta
from functools import wraps

import requests
from loguru import logger

from base import get_file_path
from db._redis import RedisClient
from db._tidb import TidbConnector
from digiCore.db.mongo.core import MongoDao

from settings import db_name


class CrawlerBase:
    def __init__(self):
        self.tidb = TidbConnector()
        self.mongo_ob=MongoDao()
        self.redis_client = RedisClient().redis_client()
        self.cookies = {}



    def get_mongodb_table(self, table_name):
        """
        从mongo读取所有 Python 对象
        传入表名，数据库名固定
        :return:循环读出的每一条字典
        """
        table_ob = self.mongo_ob.load_table_ob(db_name, table_name)
        # 计算集合中的文档数量（行数）:table_ob.count_documents({})
        # print(table_ob.count_documents({}))
        origin_data = table_ob.find()
        return origin_data

    def get_mongodb_one_month(self, table_name):
        """
        从mongo读取 20250123~20241223所有 Python 对象
        传入表名，数据库名固定
        :return:循环读出的每一条字典
        """
        # 获取当前日期时间 :
        now = datetime.now()
        # 计算一个月前的日期
        one_month_ago = now - timedelta(days=31)
        # 转换为字符串
        one_month_ago_str = one_month_ago.strftime('%Y%m%d')
        table_ob = self.mongo_ob.load_table_ob(db_name, table_name)
        filter_origin_data = table_ob.find({"dt": {"$gte": one_month_ago_str}})
        return filter_origin_data, table_ob.count_documents({"dt": {"$gte": one_month_ago_str}})

    def save_to_tidb(self, db_table, field_list, data_list):
        """
        :param db_table: 表名
        :param field_list: 字段列表
        :param data_list: 列表数据
        :return:
        """
        self.tidb.insert_data(db_table, field_list,
                              data_list)

    @staticmethod
    def timestr(unix_timestamp):
        """
        时间戳转日期：1734790378000 -->'2024-12-21 22:12:58'
        :return:
        """
        # 时间戳是到秒级，所以需要除以1000
        timestamp = unix_timestamp / 1000
        #  datetime 对象
        date_object = datetime.fromtimestamp(timestamp)
        return date_object.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def timestamp(date_object):
        """
        日期转时间戳转日期：'2024-12-21 22:12:58' -->1734790378000
        :return:
        """
        totime = datetime.strptime(date_object, '%Y-%m-%d %H:%M:%S')
        unix_timestamp = int(totime.timestamp() * 1000)
        return unix_timestamp

    @staticmethod
    def date_str(date_object):
        """
        日期字符串格式调整：'2024-12-21 22:12:58' -->'20241221'
        :return:
        """
        date_end = datetime.strptime(date_object, '%Y-%m-%d %H:%M:%S')
        date_only = date_end.date()
        date_str = date_only.strftime('%Y%m%d')
        return date_str

    @staticmethod
    def add_fields(data_list, key1, value1, key2, value2):
        """
        向列表中的每个字典添加两个键值对
        :param data_list:
        :param key1:
        :param value1:
        :param key2:
        :param value2:
        :return:
        """
        for item in data_list:
            item[key1] = value1
            item[key2] = value2
            item['skcId'] = item['skcList'][0]['skcId']
        return data_list

    @staticmethod
    def get_anti_content():
        """
        加密生成anti-content
        :return:
        """
        _ = subprocess.run(["node", get_file_path("anti_content_v8.js")], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           universal_newlines=True)
        anti_content = _.stdout.strip()
        return anti_content

    def get_code(self, pass_cookie_dict):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'cache-control': 'max-age=0',
            'anti-content': self.get_anti_content(),
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'origin': 'https://seller.kuajingmaihuo.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://seller.kuajingmaihuo.com/settle/seller-login?redirectUrl=https%3A%2F%2Fagentseller.temu.com%2Fmmsos%2Fmall-appeal.html&region=1&source=https%3A%2F%2Fagentseller.temu.com%2Fmain%2Fauthentication%3FredirectUrl%3Dhttps%253A%252F%252Fagentseller.temu.com%252Fmmsos%252Fmall-appeal.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i',
        }

        json_data = {
            'redirectUrl': 'https://agentseller.temu.com/main/authentication?redirectUrl=https%3A%2F%2Fagentseller.temu.com%2Fmmsos%2Fmall-appeal.html',
        }

        response = requests.post(
            'https://seller.kuajingmaihuo.com/bg/quiet/api/auth/obtainCode',
            cookies=pass_cookie_dict,
            headers=headers,
            json=json_data,
        )
        return response.json()['result']['code']

    def loginByCode(self, code):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'anti-content': self.get_anti_content(),
            'sec-ch-ua-platform': '"Windows"',
            'mallid': 'undefined',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'origin': 'https://agentseller.temu.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://agentseller.temu.com/main/authentication?redirectUrl=https%3A%2F%2Fagentseller.temu.com%2Fmmsos%2Fmall-appeal.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i',
        }

        json_data = {
            'code': code,
            'confirm': False,
        }

        response = requests.post(
            'https://agentseller.temu.com/api/seller/auth/loginByCode',
            # cookies=cookies,
            headers=headers,
            json=json_data,
        )
        seller_temp_cookies = dict(response.cookies)
        return seller_temp_cookies

    def userInfo(self,):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'cache-control': 'max-age=0',
            'anti-content': self.get_anti_content(),
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'origin': 'https://seller.kuajingmaihuo.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://seller.kuajingmaihuo.com/settle/seller-login?redirectUrl=https%3A%2F%2Fagentseller.temu.com%2Fmmsos%2Fmall-appeal.html&region=1&source=https%3A%2F%2Fagentseller.temu.com%2Fmain%2Fauthentication%3FredirectUrl%3Dhttps%253A%252F%252Fagentseller.temu.com%252Fmmsos%252Fmall-appeal.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i',
        }

        json_data = {}

        response = requests.post(
            'https://seller.kuajingmaihuo.com/bg/quiet/api/mms/userInfo',
            cookies=self.cookies,
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def mallId(data_dict: dict):
        """
        mallId和mallName信息的字典
        :return: mallId和mallName列表套字典
        """
        if not data_dict:
            return
        # 保存mallId和mallName的列表
        mall_info = []
        # 访问具体结构并提取信息
        company_list = data_dict["result"]["companyList"]
        for company in company_list:
            mal_info_list = company["malInfoList"]
            for mall in mal_info_list:
                mall_info.append({
                    "mallId": mall["mallId"],
                    "mallName": mall["mallName"]
                })
        return mall_info
    def main(self):
        pass



class RetryDecorator:
    @classmethod
    def retry_decorator(cls, msg=None, error_type=None, max_retry_count: int = 4, time_interval: int = 2):
        """
        任务重试装饰器
        msg:错误信息
        error_type：错误类型
        max_retry_count: 最大重试次数 默认4次
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
                        logger.error(msg if msg else f"最大重试次数{max_retry_count}： 第{retry_count+1}登录报错，正在重试！")
                        time.sleep(time_interval)
                # 如果超过最大重试次数仍未成功,则返回指定的错误类型或默认值.
                return logger.error(error_type) if error_type else f"超过最大重试次数仍未成功！"

            # 装饰器的必要结构：返回了包装原始函数的函数,实现了在函数执行前后添加额外逻辑的功能.
            return wrapper

        # 返回了装饰器函数,使得外部可以通过 @Decorate.def_retry() 的方式来调用这个装饰器.
        return _retry

    @classmethod
    def retry(cls, max_attempts: int = 2):
        """
            装饰器，用于重试指定次数
            :param max_attempts: 最大重试次数
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                attempts = 0
                while attempts < max_attempts:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                    attempts += 1
                    logger.warning(f"尝试第 {attempts} 次失败，重新尝试...")
                    time.sleep(random.choice([3.5, 3.0, 3.3, 4, 3.1, 3.2]))  # 可选：添加延迟避免频繁请求
                logger.error(f"超过最大重试次数 {max_attempts} 次，操作失败")
                return None

            return wrapper

        return decorator


if __name__ == '__main__':
    base = CrawlerBase()
    base.main()
