import random
import time
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from method.crawler_base import BaseCrawler
from pdd.db_model import ods_cd_sl_pdd_traffic_db_table, ods_cd_sl_pdd_traffic_i_d_field_list


class fetcher_pdd_trafficdata:
    """
    业绩：流量数据——成交金额
    UV：流量数据——商品访客数
    成交订单数：流量数据——成交订单数
    """
    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.cookies = ''
        self.Date = ''
        self.account = ''
        self.list_pdd_trafficdata = []

    def get_pdd_trafficdata(self):
        """采集并处理pdd流量数据"""
        headers = {
            'authority': 'mms.pinduoduo.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/json',
            'etag': 'kDiNzhtnjbBtzHFNsBzWoBdeib2PdWFA',
            'origin': 'https://mms.pinduoduo.com',
            'referer': 'https://mms.pinduoduo.com/sycm/search_data/plate?dateFlag=5&currentKey=uv&day=2024-12-10',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        json_data = {
            'beginDate': self.Date,
            'endDate': self.Date,
        }

        response = requests.post(
            'https://mms.pinduoduo.com/sydney/api/mallFlow/queryMallFlowOverView',
            cookies=self.cookies,
            headers=headers,
            json=json_data,
        )
        # 执行某些操作之间引入随机的延迟，以模拟人类行为或减轻对服务器的压力。choice:元素;choices:列表;
        time.sleep(random.choice([0.2, 0.4, 0.6]))
        if response.status_code != 200:
            return {}
        data_dict = response.json()
        try:
            trafficdata = data_dict['result']
            trafficdata['dt'] = self.Date.replace('-', '')
            trafficdata['account'] = self.account
        except Exception as e:
            logger.warning(f"pdd-流量数据 {self.Date} {self.account} 处理数据Error: {e}")
            return
        self.list_pdd_trafficdata.append(trafficdata)

    def insert_db_trafficdata(self):
        self.tidb.insert_data(ods_cd_sl_pdd_traffic_db_table, ods_cd_sl_pdd_traffic_i_d_field_list,
                              self.list_pdd_trafficdata)
        logger.info(f"pdd-流量数据 当前时间： {self.Date} {self.account} 同步 {len(self.list_pdd_trafficdata)} 完成")

    def main(self):
        jd_user_infos = self.tidb.get_user_info('PDD')
        for jd_info in jd_user_infos:
            self.account = jd_info['account']
            self.cookies = BaseCrawler().get_cookies(self.account)
            if self.cookies is None:
                continue
            dates = BaseCrawler.generate_date_list()
            for date in dates:
                self.Date = date
                self.get_pdd_trafficdata()
            self.insert_db_trafficdata()
            self.list_pdd_trafficdata = []



if __name__ == "__main__":
    fetcher = fetcher_pdd_trafficdata()
    fetcher.main()
