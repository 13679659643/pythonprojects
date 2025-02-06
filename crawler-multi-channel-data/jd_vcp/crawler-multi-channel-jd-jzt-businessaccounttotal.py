import json
import random
import time
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from jd_vcp.db_model import ods_cd_sl_jd_jzt_businessaccounttotal_db_table, ods_cd_sl_jd_jzt_businessaccounttotal_i_d_field_list
from method.crawler_base import BaseCrawler
from settings import RedisKeys


class fetcher_jd_jzt_businessaccounttotal:
    """
    京准通--搜推广告概况--账户汇总!
    """

    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.Date = ''
        self.account = ''
        self.data_list = []
        self.cookies = ''

    def get_cookies(self):
        redis_key = f"{RedisKeys.JD_LOGIN_KEY.value}:{self.account}"
        jd_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not jd_cookie:
            logger.info(f"京东自营京淮通--B端营销--账户投放概况--账户汇总 cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        jd_cookie_dict = json.loads(jd_cookie)
        return jd_cookie_dict

    def fetch_page_data(self):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""
        headers = {
            'authority': 'atoms-api.jd.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'language': 'zh_CN',
            'loginmode': '0',
            'origin': 'https://jbm.jd.com',
            'referer': 'https://jbm.jd.com/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'siteid': '13',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        json_data = {
            'clickOrOrderDay': 30,
            'grantStatus': 0,
            'dataType': 1,
            'startDay': self.Date,
            'endDay': self.Date,
            'granularity': 1,
        }

        response = requests.post('https://atoms-api.jd.com/reweb/jaguar/common/trend', cookies=self.cookies, headers=headers,
                                 json=json_data)
        # 执行某些操作之间引入随机的延迟，以模拟人类行为或减轻对服务器的压力。choice:元素;choices:列表;
        time.sleep(random.choice([0.2, 0.4, 0.6]))
        if response.status_code != 200:
            return {}
        # json.dumps() 是 Python json 模块的一个函数，它将 Python 对象转换（序列化）为 JSON 格式的字符串。
        return response.json()

    def process_data(self, page_data: dict):
        """处理每天的数据"""
        try:
            page_data = page_data['data']['ext']
            page_data['dt'] = self.Date
        except Exception as e:
            logger.warning(f"京东自营京淮通--B端营销--账户投放概况--账户汇总 {self.Date} {self.account} 处理数据Error: {e}")
            return
        self.data_list.append(page_data)

    def get_jd_jzt_data(self):
        self.tidb.insert_data(ods_cd_sl_jd_jzt_businessaccounttotal_db_table, ods_cd_sl_jd_jzt_businessaccounttotal_i_d_field_list,
                              self.data_list)
        logger.info(f"京东自营京淮通--B端营销--账户投放概况--账户汇总 当前时间：{self.Date} {self.account} 同步 {len(self.data_list)} 完成")

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
                self.process_data(data_dict)
        self.get_jd_jzt_data()


if __name__ == "__main__":
    fetcher = fetcher_jd_jzt_businessaccounttotal()
    fetcher.main()
