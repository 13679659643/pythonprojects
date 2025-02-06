import random
import time
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from method.crawler_base import BaseCrawler
from pdd.db_model import ods_cd_sl_pdd_promotional_db_table, ods_cd_sl_pdd_promotional_i_d_field_list
from urllib.parse import quote_plus


class fetcher_pdd_promotional:
    """
    https://mms.pinduoduo.com/login/?redirectUrl=https%3A%2F%2Fmms.pinduoduo.com%2F
    退款额：服务数据——售后数据——成功退款金额
    """

    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.cookies = ''
        self.Date = ''
        self.account = ''
        self.list_pdd_promotional = []
        self.anti_content = ''
        self.accessToken = ''
        self.sub_pass_id = ''
        self.mall_id = ''
        self.sub_pass_cookies = {}

    def get_pdd_accessToken(self):
        """采集并处理pdd-推广平台-商品推广-总花费"""
        headers = {
            'authority': 'mms.pinduoduo.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'anti-content': self.anti_content,
            'cache-control': 'max-age=0',
            'content-type': 'application/json',
            'etag': 'kDiNzhtnjbBtzHFNsBzWoBdeib2PdWFA',
            'origin': 'https://mms.pinduoduo.com',
            'referer': 'https://mms.pinduoduo.com/login/?redirectUrl=https%3A%2F%2Fyingxiao.pinduoduo.com%2Fmains%2FpromotionOverview&platform=yingxiao',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        json_data = {
            'redirectUrl': 'https://yingxiao.pinduoduo.com/mains/promotionOverview',
        }
        response = requests.post(
            'https://mms.pinduoduo.com/janus/api/subSystem/generateAccessToken',
            cookies=self.cookies,
            headers=headers,
            json=json_data,
        )
        response = response.json()
        accessToken = response['result']['accessToken']
        return accessToken

    def get_pdd_token(self):
        """采集并处理pdd-推广平台-商品推广-总花费"""
        username = quote_plus(self.account)
        headers = {
            'authority': 'yingxiao.pinduoduo.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://yingxiao.pinduoduo.com',
            'referer': f'https://yingxiao.pinduoduo.com/mains/promotionOverview?accessToken={self.accessToken}&username={username}',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        json_data = {
            'accessToken': self.accessToken,
            'subSystemId': 7,
        }
        response = requests.post(
            'https://yingxiao.pinduoduo.com/mms-gateway/user/getToken',
            cookies=self.cookies,
            headers=headers,
            json=json_data,
        )
        SUB_PASS_ID = dict(response.cookies)['SUB_PASS_ID']
        return SUB_PASS_ID

    def get_pdd_id(self):
        """采集并处理pdd-推广平台-商品推广-总花费"""
        headers = {
            'authority': 'yingxiao.pinduoduo.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'anti-content': self.anti_content,
            'content-type': 'application/json',
            'origin': 'https://yingxiao.pinduoduo.com',
            'referer': 'https://yingxiao.pinduoduo.com/goods/report/promotion/overView?beginDate=2024-12-01&endDate=2024-12-01',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }

        self.sub_pass_cookies = {
            'SUB_PASS_ID': self.sub_pass_id,
        }
        response = requests.post('https://yingxiao.pinduoduo.com/mms-gateway/user/info', cookies=self.sub_pass_cookies,
                                 headers=headers)
        mall_id = response.json()['result']['mall']['mall_id']
        return mall_id


    def get_pdd_promotional(self):
        """采集并处理pdd-推广平台-商品推广-总花费"""
        headers = {
            'authority': 'yingxiao.pinduoduo.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'anti-content': self.anti_content,
            'content-type': 'application/json',
            'origin': 'https://yingxiao.pinduoduo.com',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        json_data = {
            'crawlerInfo': self.anti_content,
            'entityId': self.mall_id,
            'entityDimensionType': 0,
            'queryDimensionType': 2,
            'reportPromotionType': 9,
            'startDate': self.Date,
            'endDate': self.Date,
            'query': {
                'fieldToValue': {},
            },
            'returnTotalSumReport': True,
        }
        response = requests.post(
            'https://yingxiao.pinduoduo.com/mms-gateway/apollo/api/report/queryEntityReport',
            cookies=self.sub_pass_cookies,
            headers=headers,
            json=json_data,
        )
        # 执行某些操作之间引入随机的延迟，以模拟人类行为或减轻对服务器的压力。choice:元素;choices:列表;
        time.sleep(random.choice([0.8, 1, 1.2]))
        if response.status_code != 200:
            return {}
        data_dict = response.json()
        try:
            promotionaldata = data_dict['result']['totalSumReport']
            promotionaldata['dt'] = self.Date.replace('-', '')
            promotionaldata['account'] = self.account
            promotionaldata['spend'] = promotionaldata['spend'] / 1000
            promotionaldata['liveCostPerOrder'] = promotionaldata['liveCostPerOrder'] / 1000
            promotionaldata['orderSpend'] = promotionaldata['orderSpend'] / 1000
            promotionaldata['avgPayAmount'] = promotionaldata['avgPayAmount'] / 1000
            promotionaldata['gmv'] = promotionaldata['gmv'] / 1000
        except Exception as e:
            logger.warning(f"pdd-推广平台-商品推广-总花费 {self.Date} {self.account} 处理数据Error: {e}")
            return
        self.list_pdd_promotional.append(promotionaldata)

    def insert_db_promotional(self):
        self.tidb.insert_data(ods_cd_sl_pdd_promotional_db_table, ods_cd_sl_pdd_promotional_i_d_field_list,
                              self.list_pdd_promotional)
        logger.info(
            f"pdd-推广平台-商品推广-总花费 当前时间： {self.Date} {self.account} 同步 {len(self.list_pdd_promotional)} 完成")

    def main(self):
        jd_user_infos = self.tidb.get_user_info('PDD')
        for jd_info in jd_user_infos:
            self.account = jd_info['account']
            self.cookies = BaseCrawler().get_cookies(self.account)
            if self.cookies is None:
                continue
            self.anti_content = BaseCrawler().get_anti_content()
            self.accessToken = self.get_pdd_accessToken()
            self.sub_pass_id = self.get_pdd_token()
            self.mall_id = self.get_pdd_id()
            dates = BaseCrawler.generate_date_list()
            for date in dates:
                self.Date = date
                self.anti_content = BaseCrawler().get_anti_content()
                self.get_pdd_promotional()
            self.insert_db_promotional()
            self.list_pdd_promotional = []


if __name__ == "__main__":
    fetcher = fetcher_pdd_promotional()
    fetcher.main()
