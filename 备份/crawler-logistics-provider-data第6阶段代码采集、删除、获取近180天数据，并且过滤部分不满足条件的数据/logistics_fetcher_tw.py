# -*- coding: utf-8 -*-
# @Time    : 2024/8/9 15:34
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:
import redis
import requests
from bs4 import BeautifulSoup
from loguru import logger
from lxml import etree

from crawler_base import BaseCrawler
from method import RetryDecorator, create_insert_sql, DatabaseConnector


class LogisticsDataFetcher_tw(BaseCrawler):
    def __init__(self, ):
        super().__init__()
        self.session = requests.session()
        # 在这里，self.session.headers 是一个字典，.update({...}) 方法用于向这个字典中添加或更新键值对
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        })

    def get_auth_cookies(self):
        """从 Redis 获取或请求新的认证 token，使用哈希存储多个键值对"""
        with self.redis_client.conn as redis_client:
            if not redis_client.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                params = {
                    'action': 'logon',
                }
                data = {
                    'userid': self.config[self.logistics_provider_code]['username'],
                    'password': self.config[self.logistics_provider_code]['password'],
                }
                response = self.session.post(self.token_url, data=data, params=params)
                # 检查请求是否成功。如果请求返回的状态码不是 2xx，会抛出一个 HTTPError 异常：response.raise_for_status()
                if response.status_code == 200:
                    # 获取会话中的 cookies
                    cookies = self.session.cookies
                    # 将 cookies 转换为字典（可选）
                    cookies_dict = requests.utils.dict_from_cookiejar(cookies)
                    # 使用字典的 items() 方法获取所有的键值对，然后使用字符串的 format 方法格式化字符串
                    cookies_str = "; ".join(["{}={}".format(k, v) for k, v in cookies_dict.items()])
                    # 设置哈希存储键值对：将 token 存储到 Redis 中
                    redis_client.hset(self.HASH_AUTH_TOKEN, self.key, cookies_str)
                    # 使用单独的键存储过期时间：并设置过期时间为86400s即1天
                    redis_client.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 2 * 60 * 60, "1")
                    logger.info("天伟-登录cookies获取成功")
                else:
                    logger.warning(f"登录请求失败，状态码：{response.status_code}")
                    return None
            # 获取哈希字段的值：返回 Redis 中 名称为key的string的value
            return redis_client.hget(self.HASH_AUTH_TOKEN, self.key)

    @RetryDecorator.retry_decorator(msg="采集数据出错", error_type=713, max_retry_count=3, time_interval=1)
    def fetch_page_data(self, page=1):
        """
        获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后
        :param page:
        :return: html:str
        """
        params = {
            'action': 'getOrderList',
            'pageflag': '1',
        }
        data = {
            'orderField': 'a.billid',
            'orderDirection': 'asc',
            'numPerPage': '20',
            'pageNum': page,
        }
        response = self.session.post('https://tw.kingtrans.net/nclient/CCOrder', params=params, data=data)
        if response.status_code != 200:
            logger.info(f"当前第 {page} 页，数据请求出错。" )
            return ''
        return response.text

    def get_total_page(self, html):
        """
        获取需要爬取的最大页数
        :param html:
        :return: int
        """
        parser = etree.HTMLParser()
        tree = etree.fromstring(html, parser)
        # 获取 id 为 pageRecordCount 的元素的文本内容
        total_rows = tree.xpath('//*[@id="pageRecordCount"]/text()')[0]
        total_pages = (int(total_rows) + 20 - 1) // 20
        return total_pages

    # 解析 HTML 并提取 sid_billstatus_sid 数据
    def parse_html(self, html):
        """
        #解析 HTML 并提取 sid_billstatus_sid 数据
        :param html:
        :return:[[],[]]
        """
        # 创建一个 HTML 解析器
        parser = etree.HTMLParser()
        # 使用这个解析器来解析字符串，生成一个元素树。
        tree = etree.fromstring(html, parser)
        # 获取所有 target 属性为 sid_billstatus_sid 的 tr 元素
        rows = tree.xpath('//tr[@target="sid_billstatus_sid"]')
        data = []
        for row in rows:
            # 获取当前元素（即 tr 元素）下的所有 td 元素，除了第一个。
            row_data = [td.text.strip() for td in row.xpath('./td[position()>1]')]
            data.append(row_data)
        return data

    def fetch_all_data(self, total_pages: int):
        """
        获取所有页的数据
        :param total_pages:
        :return: [[],[]]
        """
        # 循环处理每一页
        all_data = []
        for page_num in range(1, total_pages + 1):
            html = self.fetch_page_data(page_num)
            if not html:
                continue
            page_data = self.parse_html(html)
            all_data.extend(page_data)
        logger.info(f'当前数据采集 {self.logistics_provider} 采集完成.len: {len(all_data)}')
        return all_data

    def process_data(self, data_list: [list]):
        """
        将二维列表转换为所需格式的字符串，并在每个元组后面添加 '0'。
        :param data_list:
        :param : 要转换的二维列表
        :return: str: "(),()"
        ','.join(f"'{item}'" for item in row)-->将每个元素包裹在单引号中，并用逗号连接
        "({})".format()-->将上述字符串放入括号中
        ','.join(...)---->将所有行处理后的字符串用逗号连接，形成最终的字符串表示
        """
        formatted_data = ','.join(
            "({})".format(', '.join(f"'{item}'" for item in row) + ", '0'")
            for row in data_list
        )
        return formatted_data

    def insert_data_to_db(self, db_table: str, field_list: list, sql_values: str):
        """创建和插入数据到数据库"""

        # with 语句结合上下文管理器模式:默认情况下，许多数据库连接库（包括 pymysql）在连接时会自动开启一个事务
        with DatabaseConnector() as db_connector:
            connection = db_connector.connection
            with connection.cursor() as cursor:
                cursor.execute(self.create_table_query)
                cursor.execute(self.truncate_table_query)
                insert_sql = create_insert_sql(db_table, field_list, sql_values)
                cursor.execute(insert_sql)
                logger.info(f'插入完成')

    def main(self):
        self.init_logistic("K5")
        self.session.headers['Cookie'] = self.get_auth_cookies()
        html = self.fetch_page_data()
        if not html:
            return
        total_page = self.get_total_page(html)
        data_list = self.fetch_all_data(total_page)
        sql_values = self.process_data(data_list)
        if not sql_values:
            return
        self.insert_data_to_db(self.db_table, self.table_field_list, sql_values)


if __name__ == "__main__":
    # 创建 LogisticsDataFetcher_nextsls 类的一个实例 fetcher
    fetcher = LogisticsDataFetcher_tw()
    # 调用 fetcher 的 run 方法开始执行数据抓取任务
    fetcher.main()
