import random
import time
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from method.crawler_base import BaseCrawler
from pdd.db_model import ods_cd_sl_pdd_sales_db_table, ods_cd_sl_pdd_sales_i_d_field_list


class fetcher_pdd_sales:
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
        self.list_pdd_sales = []

    def get_pdd_sales(self):
        """采集并处理pdd-服务数据-售后数据—成功退款金额"""
        headers = {
            'authority': 'mms.pinduoduo.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'anti-content': '0asWfxUeM_Ve0a-Wg0V2AQ8x3bn550BSIWW09HYjsPcnUlGpVIGHCdjuJQXiwKqNjfGNbsPXYFtzrRbnU-ETYytTLvboH9ynpWY1sPtfmvFndT6T57xflvcfY6Aj-wcfm6pjOU9qgdEygUEas9chmpKG07ox0hjyHeV1NwYHqY6oq5-GGVFJY4EwCo1E5W621BCE23qfOeM_Me7kVDMkKkM35eBwlJMx5mB_VD7_FmMxZe20wb_ALb-YF5OYGaOkGYPiN8oqOYfpAwJjdlwy9V6hUBtosU2Xyd2yg0TasK2GB2MeIjwe7D5IW2evf4dB1LD3fjkKMiImG3SmGDVbWy_bhhUK34dMk8IbfLDSf8oIW4uvkpCML1oDBpKka444OBfDe-sMz9c0_K_2mMsgeEQ5EFsGez3Zp63gurxA7rx_k3MZFDsQer1EIsZWDFMhvDf6vpHSG49Q3xYNcnYNtwEp0ZSQxhLhLAgM9ubBjDvQyveWjw3QDmm8IruOPjxNcMMcAaEBBbaTM259V9U91c6p1dRYat',
            'cache-control': 'max-age=0',
            'content-type': 'application/json',
            'etag': 'kDiNzhtnjbBtzHFNsBzWoBdeib2PdWFA',
            'origin': 'https://mms.pinduoduo.com',
            'referer': 'https://mms.pinduoduo.com/sycm/goods_quality/detail?dateFlag=5&day=2024-12-15&currentKey=sucRfOrdrAmt1d',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        json_data = {
            'queryDate': self.Date,
        }

        response = requests.post(
            'https://mms.pinduoduo.com/sydney/api/saleQuality/querySaleQualityDetailInfo',
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
            salesdata = data_dict['result']
            salesdata['dt'] = self.Date.replace('-', '')
            salesdata['account'] = self.account
        except Exception as e:
            logger.warning(f"pdd-服务数据-售后数据—成功退款金额 {self.Date} {self.account} 处理数据Error: {e}")
            return
        self.list_pdd_sales.append(salesdata)

    def insert_db_sales(self):
        self.tidb.insert_data(ods_cd_sl_pdd_sales_db_table, ods_cd_sl_pdd_sales_i_d_field_list,
                              self.list_pdd_sales)
        logger.info(f"pdd-服务数据-售后数据—成功退款金额 当前时间： {self.Date} {self.account} 同步 {len(self.list_pdd_sales)} 完成")

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
                self.get_pdd_sales()
            self.insert_db_sales()
            self.list_pdd_sales = []


if __name__ == "__main__":
    fetcher = fetcher_pdd_sales()
    fetcher.main()
