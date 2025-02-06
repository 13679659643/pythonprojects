import json
from datetime import datetime, timedelta
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from jd_vcp.db_model import ods_cd_sl_jd_performance_db_table, ods_cd_sl_jd_performance_i_d_field_list
from method.crawler_base import BaseCrawler
from settings import RedisKeys
from pprint import pprint


class fetcher_jd_vcp_performance:
    """
    业绩:VC后台--数据管理--商品业绩--导出第1天数据--成本
    退款额:VC后台--数据管理--商品业绩--导出第1天数据--成本下拉到底-负数金额
    """
    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        # self.tidb_client = TiDBDao('192.168.0.201')
        self.startDate = '2024-11-01'
        self.endDate = '2024-11-30'
        self.Date = ''
        self.cookies = ''
        self.account = ''

    def get_cookies(self):
        redis_key = f"{RedisKeys.JD_LOGIN_KEY.value}:{self.account}"
        jd_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not jd_cookie:
            logger.info(f"京东自营--VC后台--数据管理--商品业绩 cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        jd_cookie_dict = json.loads(jd_cookie)
        return jd_cookie_dict

    def fetch_page_data(self, page=1):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""
        headers = {
            'authority': 'sff.jd.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json; charset=UTF-8',
            'dsm-platform': 'pc',
            'origin': 'https://vc-performance.jd.com',
            'referer': 'https://vc-performance.jd.com/',
            'requestid': '1732602205184_0.3987726697020342',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        params = {
            'v': '1.0',
            'appId': 'NLHURQLE9ZBXBMMYVJRT',
            'api': 'dsm.open.gatway.preformance.queryProductPerformanceList',
        }
        json_data = {
            'param': {
                'startDate': self.Date,
                'endDate': self.Date,
                'pageNum': page,
                'pageSize': 50,
            },
        }
        response = requests.post(
            'https://sff.jd.com/api',
            params=params,
            headers=headers,
            cookies=self.cookies,
            json=json_data,
        )
        if response.status_code != 200:
            return {}
        # print(response.json())
        return response.json()

    def fetch_all_data(self, data_dict: dict):
        """顺序获取所有页的数据"""
        if not data_dict:
            return []
        elif not data_dict['data']['data']:
            logger.info(f"VC后台--数据管理--商品业绩 {self.Date} 业绩页面无数据")
            return []
        # 获取总行数（total_rows）和每页的大小（page_size）
        total_rows = data_dict['data']['total']
        page_size = 50
        # 将总行数加上每页大小减一,然后整除每页大小来完成的.这样做是为了确保如果总行数不能被每页大小整除时,总页数会向上取整.
        total_pages = (total_rows + page_size - 1) // page_size
        total_page_data = []
        for page in range(1, total_pages + 1):
            try:
                page_data = self.fetch_page_data(page)
                total_page_data.append(page_data)
            except Exception as e:
                logger.error(f'------- 任务执行中发生了异常: {e} -------')
        return total_page_data

    def process_data(self, total_page_data: list[dict]):
        """处理每页的数据"""
        processed_data_all = []
        for page_data in total_page_data:
            page_dataSource = page_data['data']['data']
            try:
                for item in page_dataSource:
                    item["dt"] = self.Date
                    # 　get() 方法接受两个参数：键和默认值。如果字典中存在这个键，get() 方法会返回这个键对应的值；如果字典中不存在这个键，get() 方法会返回默认值。
            except Exception as e:
                logger.warning(f"处理数据Error: {e}")
            processed_data_all.extend(page_dataSource)
        return processed_data_all

    def get_jd_vcp_data(self, processed_data_all: list[dict]):
        self.tidb.insert_data(ods_cd_sl_jd_performance_db_table, ods_cd_sl_jd_performance_i_d_field_list,
                              processed_data_all)
        logger.info(f"VC后台--数据管理--商品业绩 {self.Date} 同步 {len(processed_data_all)} 完成")

    def main(self):
        jd_user_infos = self.tidb.get_user_info('JD')
        for jd_info in jd_user_infos:
            self.account = jd_info['account']
            self.cookies = self.get_cookies()
            if self.cookies is None:
                continue
            dates = BaseCrawler.generate_date_list()
            for date in dates:
                self.Date = date
                data_dict = self.fetch_page_data()
                total_page_data = self.fetch_all_data(data_dict)
                processed_data_all = self.process_data(total_page_data)
                self.get_jd_vcp_data(processed_data_all)



if __name__ == "__main__":
    fetcher = fetcher_jd_vcp_performance()
    fetcher.main()
