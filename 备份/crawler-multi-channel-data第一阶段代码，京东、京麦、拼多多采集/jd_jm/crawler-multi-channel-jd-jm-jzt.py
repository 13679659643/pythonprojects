import json
from datetime import datetime, timedelta
import random
import time

import execjs
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from jd_jm.db_model import ods_cd_sl_jd_jm_paymentcommissions_db_table, ods_cd_sl_jd_jm_paymentcommissions_i_d_field_list, \
    ods_cd_sl_jd_jm_adaccounttotal_db_table, ods_cd_sl_jd_jm_adaccounttotal_i_d_field_list, \
    ods_cd_sl_jd_jm_salestotal_db_table, ods_cd_sl_jd_jm_salestotal_i_d_field_list
from method.crawler_base import BaseCrawler
from settings import RedisKeys
from pprint import pprint


class fetcher_jd_jm_jzt:
    """
    <1>京准通——搜推广告概况——账户汇总
    <2>京准通--全站营销概况--账户汇总
    <3>京准通——京东联盟——（选择日期）——付款佣金
    """
    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.cookies = ''
        self.Date = ''
        self.account = ''
        self.data_list_adaccounttotal = []
        self.data_list_salestotal = []
        self.data_list_paymentcommissions = []
        self.jzthome_headers = {
            'authority': 'atoms-api.jd.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'language': 'zh_CN',
            'loginmode': '0',
            'origin': 'https://jzt.jd.com',
            'referer': 'https://jzt.jd.com/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'siteid': '0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        self.adaccounttotal_json_data = {}
        self.salestotal_json_data = {}
        self.jzthome_url = 'https://atoms-api.jd.com/reweb/common/indicator'
        self.paymentcommissions_json_data = {}
        self.jdalliance_url = 'https://jzt-api.jd.com/union/dataAnalyze/trend?requestFrom=0'

    def get_cookies(self):
        redis_key = f"{RedisKeys.JD_JM_LOGIN_KEY.value}:{self.account}"
        jm_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not jm_cookie:
            logger.info(f"京麦 {self.account} cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        jm_cookie_dict = json.loads(jm_cookie)
        return jm_cookie_dict

    def adaccounttotal_data(self):
        """京准通--搜推广告概况--账户汇总!"""
        response = requests.post(self.jzthome_url, cookies=self.cookies,
                                 headers=self.jzthome_headers,
                                 json=self.adaccounttotal_json_data)
        # 执行某些操作之间引入随机的延迟，以模拟人类行为或减轻对服务器的压力。choice:元素;choices:列表;
        time.sleep(random.choice([0.2, 0.4, 0.6]))
        if response.status_code != 200:
            return {}
        data_dict = response.json()
        try:
            page_data = data_dict['data']
            page_data['dt'] = self.Date
            page_data['account'] = self.account
        except Exception as e:
            logger.warning(f"朗盟京麦京准通--搜推广告概况--账户汇总 {self.Date} {self.account} 处理数据Error: {e}")
            return
        self.data_list_adaccounttotal.append(page_data)

    def salestotal_data(self):
        """京准通--全站营销概况--账户汇总!"""
        response = requests.post(self.jzthome_url, cookies=self.cookies,
                                 headers=self.jzthome_headers,
                                 json=self.salestotal_json_data)
        time.sleep(random.choice([0.2, 0.4, 0.6]))
        if response.status_code != 200:
            return {}
        data_dict = response.json()
        try:
            page_data = data_dict['data']
            page_data['dt'] = self.Date
            page_data['account'] = self.account
        except Exception as e:
            logger.warning(f"朗盟京麦京准通--全站营销概况--账户汇总 {self.Date} {self.account} 处理数据Error: {e}")
            return
        self.data_list_salestotal.append(page_data)

    def paymentcommissions_data(self):
        """京准通--全站营销概况--账户汇总!"""
        response = requests.post(self.jdalliance_url, cookies=self.cookies,
                                 headers=self.jzthome_headers,
                                 json=self.paymentcommissions_json_data)
        time.sleep(random.choice([0.2, 0.4, 0.6]))
        if response.status_code != 200:
            return {}
        data_dict = response.json()
        try:
            page_data = data_dict['content']['list2Total']
            page_data['dt'] = self.Date
            page_data['account'] = self.account
        except Exception as e:
            logger.warning(f"朗盟京麦京准通-京东联盟-付款佣金 {self.Date} {self.account} 处理数据Error: {e}")
            return
        self.data_list_paymentcommissions.append(page_data)

    def insert_db_adaccounttotal(self):
        self.tidb.insert_data(ods_cd_sl_jd_jm_adaccounttotal_db_table, ods_cd_sl_jd_jm_adaccounttotal_i_d_field_list,
                              self.data_list_adaccounttotal)
        logger.info(f"朗盟京麦京准通--搜推广告概况--账户汇总 当前时间：{self.Date}  同步 {len(self.data_list_adaccounttotal)} 完成")

    def insert_db_salestotal(self):
        self.tidb.insert_data(ods_cd_sl_jd_jm_salestotal_db_table, ods_cd_sl_jd_jm_salestotal_i_d_field_list,
                              self.data_list_salestotal)
        logger.info(f"朗盟京麦京准通--全站营销概况--账户汇总 当前时间：{self.Date}  同步 {len(self.data_list_salestotal)} 完成")

    def insert_db_paymentcommissions(self):
        self.tidb.insert_data(ods_cd_sl_jd_jm_paymentcommissions_db_table, ods_cd_sl_jd_jm_paymentcommissions_i_d_field_list,
                              self.data_list_paymentcommissions)
        logger.info(f"朗盟京麦京准通-京东联盟-付款佣金 当前时间：{self.Date} 同步 {len(self.data_list_paymentcommissions)} 完成")

    def main(self):
        jd_user_infos = self.tidb.get_user_info('JD-JM')
        for jd_info in jd_user_infos:
            self.account = jd_info['account']
            self.cookies = self.get_cookies()
            if self.cookies is None:
                continue
            dates = BaseCrawler.generate_date_list()
            for date in dates:
                self.Date = date
                self.adaccounttotal_json_data = {
                    'startDay': f'{self.Date} 00:00:00',
                    'endDay': f'{self.Date} 23:59:59',
                    'businessType': -1,
                    'mediaResourceType': None,
                    'interactiveType': None,
                    'clickOrOrderDay': 15,
                    'clickOrOrderCaliber': 0,
                    'orderStatusCategory': None,
                    'giftFlag': 0,
                }
                self.salestotal_json_data = {
                    'startDay': f'{self.Date} 00:00:00',
                    'endDay': f'{self.Date} 23:59:59',
                    'businessType': 600000004,
                    'mediaResourceType': None,
                    'interactiveType': None,
                    'clickOrOrderDay': 15,
                    'clickOrOrderCaliber': 0,
                    'orderStatusCategory': 1,
                    'giftFlag': None,
                }
                self.paymentcommissions_json_data = {
                    'startDate': self.Date,
                    'endDate': self.Date,
                    'realTime': False,
                    'deliveryModeType': None,
                }
                self.adaccounttotal_data()
                self.salestotal_data()
                self.paymentcommissions_data()
        self.insert_db_adaccounttotal()
        self.insert_db_salestotal()
        self.insert_db_paymentcommissions()


if __name__ == "__main__":
    fetcher = fetcher_jd_jm_jzt()
    fetcher.main()
