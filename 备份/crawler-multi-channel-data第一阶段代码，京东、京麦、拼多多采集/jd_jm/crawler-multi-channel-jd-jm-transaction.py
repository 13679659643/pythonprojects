import json
from datetime import datetime, timedelta

import execjs
import requests
from loguru import logger
from jd_jm import get_file_path
from db._redis import RedisClient
from db._tidb import TidbConnector
from jd_jm.db_model import ods_cd_sl_jd_jm_transaction_db_table, ods_cd_sl_jd_jm_transaction_i_d_field_list
from method.crawler_base import BaseCrawler
from settings import RedisKeys
from pprint import pprint


class fetcher_jd_jm_transaction:
    """
    业绩：京东商智——交易——交易概况——成交金额（需扣除操作金额）
    订单量：京东商智--交易--交易概况--成交单量
    UV：京东商智——交易——交易概况——访客数
    退款额：京东商智——交易——交易概况——（取消及售后退款金额 扣除 订单列表：当天未发货申请退款的金额）
    """
    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        # self.tidb_client = TiDBDao('192.168.0.201')
        self.Date = ''
        self.account = ''
        self.data_list = []
        self.cookies = {}

    def get_cookies(self):
        redis_key = f"{RedisKeys.JD_JM_LOGIN_KEY.value}:{self.account}"
        jm_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not jm_cookie:
            logger.info(f"京麦--京东商智--交易--交易概况 cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        jm_cookie_dict = json.loads(jm_cookie)
        return jm_cookie_dict

    def fetch_page_data(self):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""
        with open(get_file_path('fronted_monitor.js'), 'r', encoding='utf-8') as f:
            js = f.read()
        context = execjs.compile(js)
        cookie_str = '; '.join([f"{name}={value}" for name, value in self.cookies.items()])
        uuid, user_mup, user_mnp = context.call('get_ajax_au_header', '/sz/api/trade/getSummaryData.ajax',
                                                'https://sz.jd.com/sz/view/dealAnalysis/dealSummarys.html',
                                                cookie_str)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Referer': 'https://sz.jd.com/sz/view/dealAnalysis/dealSummarys.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
            'User-mnp': user_mnp,
            'User-mup': str(user_mup),
            'X-Requested-With': 'XMLHttpRequest',
            'p-pin': self.cookies['pin'],
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'uuid': uuid,
        }

        params = {
            'channel': '99',
            'cmpType': '0',
            # 'date': '2024-11-28',
            'endDate': self.Date,
            'startDate': self.Date,
        }
        response = requests.get(
            'https://sz.jd.com/sz/api/trade/getSummaryData.ajax',
            params=params,
            headers=headers,
            cookies=self.cookies,
        )
        if response.status_code != 200:
            return {}
        # pprint(response.json())
        # exit()
        return response.json()

    def process_data(self, page_data: dict):
        """处理每页的数据"""
        value_dict = {}
        try:
            for key, sub_dict in page_data['content'].items():
                value_dict[key] = sub_dict['value']
            value_dict['dt'] = self.Date
            value_dict['account'] = self.account
        except Exception as e:
            if page_data['status'] == -1 and page_data['message'] == 'valid menuOpen is error':
                logger.info(f"京麦--京东商智--交易--交易概况 {self.Date} {self.account} 这一天页面无数据。")
                return
            else:
                logger.warning(f"京麦--京东商智--交易--交易概况 {self.Date} {self.account} 处理数据Error: {e}")
                return
        # 　get() 方法接受两个参数：键和默认值。如果字典中存在这个键，get() 方法会返回这个键对应的值；如果字典中不存在这个键，get() 方法会返回默认值。
        self.data_list.append(value_dict)

    def get_jd_jm_data(self):
        self.tidb.insert_data(ods_cd_sl_jd_jm_transaction_db_table, ods_cd_sl_jd_jm_transaction_i_d_field_list,
                              self.data_list)
        logger.info(f"京麦--京东商智--交易--交易概况 当前时间：{self.Date} {self.account} 同步 {len(self.data_list)} 完成")

    def main(self):
        jd_JM_user_infos = self.tidb.get_user_info('JD-JM')
        for jd_jm_info in jd_JM_user_infos:
            self.account = jd_jm_info['account']
            self.cookies = self.get_cookies()
            if self.cookies is None:
                continue
            dates = BaseCrawler.generate_date_list()
            for date in dates:
                self.Date = date
                data_dict = self.fetch_page_data()
                self.process_data(data_dict)
        self.get_jd_jm_data()



if __name__ == "__main__":
    fetcher = fetcher_jd_jm_transaction()
    fetcher.main()
