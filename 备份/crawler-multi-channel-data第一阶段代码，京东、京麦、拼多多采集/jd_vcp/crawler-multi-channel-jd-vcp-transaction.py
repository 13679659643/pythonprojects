import json
from datetime import datetime, timedelta
from loguru import logger

from jd_vcp import get_file_path
from db._redis import RedisClient
from db._tidb import TidbConnector
from jd_vcp.db_model import ods_cd_sl_jd_transaction_db_table, ods_cd_sl_jd_transaction_i_d_field_list
from pprint import pprint
import execjs
import requests

from method.crawler_base import BaseCrawler
from settings import RedisKeys


class fetcher_jd_vcp_transaction:
    """
    UV:VC后台--品牌纵横--交易--交易概况--访客数
    订单量：VC后台--品牌纵横--交易--交易概况--成交单量
    """
    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.Date = ''
        self.data_list = []
        self.cookies = {}
        self.account = ''

    def get_cookies(self):
        redis_key = f"{RedisKeys.JD_LOGIN_KEY.value}:{self.account}"
        jd_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not jd_cookie:
            logger.info(f"朗盟京东自营-VC后台--品牌纵横--交易--交易概况 cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        jd_cookie_dict = json.loads(jd_cookie)
        return jd_cookie_dict

    def fetch_page_data(self, page=1):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""

        with open(get_file_path('jd_fronted_monitor.js'), 'r', encoding='utf-8') as f:
            js = f.read()
        context = execjs.compile(js)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Referer': 'https://sz.jd.com/sz/view/dealAnalysis/dealSummarys.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
            'X-Requested-With': 'XMLHttpRequest',
            'p-pin': self.cookies['pin'],
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        uuid, user_mup, user_mnp = context.call('get_ajax_au_header',
                                                'https://ppzh.jd.com/brand/dealAnalysis/dealDetail/getDealDetailData.ajax')
        # 京东概括
        params = {
            'thirdCategoryId': 'all',
            'brandId': 'all',
            'channel': '0',
            'shopType': 'all',
            # 'date': '102024-11-29',
            'endDate': self.Date,
            'startDate': self.Date,
            'pageSize': '50',
            'pageNum': page,
            'User-mup': user_mup,
            'User-mnp': user_mnp,
            'uuid': uuid,
        }
        response = requests.get(
            'https://ppzh.jd.com/brand/dealAnalysis/dealDetail/getDealDetailData.ajax',
            params=params,
            cookies=self.cookies,
            headers=headers,
        )
        if response.status_code != 200:
            return {}
        return response.json()

    def fetch_all_data(self, data_dict: dict):
        """顺序获取所有页的数据"""
        # 当前天无数据也会返回response.json() [200]
        if not data_dict:
            return []
        elif not data_dict['content']:
            logger.info(f"朗盟京东自营-VC后台--品牌纵横--交易--交易概况 {self.Date} 交易明细页面无数据")
            return []
        # 获取总行数（total_rows）和每页的大小（page_size）
        total_rows = data_dict['content']['totalNum']
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
            page_dataSource = page_data['content']['data']
            try:
                for item in page_dataSource:
                    item["dt"] = self.Date
                    # 　get() 方法接受两个参数：键和默认值。如果字典中存在这个键，get() 方法会返回这个键对应的值；如果字典中不存在这个键，get() 方法会返回默认值。
            except Exception as e:
                logger.warning(f"处理数据Error: {e}")
            processed_data_all.extend(page_dataSource)
        self.data_list.extend(processed_data_all)

    def get_jd_vcp_data(self):
        self.tidb.insert_data(ods_cd_sl_jd_transaction_db_table, ods_cd_sl_jd_transaction_i_d_field_list,
                              self.data_list)
        logger.info(f"朗盟京东自营-VC后台--品牌纵横--交易--交易概况 当前时间：{self.Date} 同步 {len(self.data_list)} 完成")

    def main(self):
        # [dist]
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
                self.process_data(total_page_data)
        self.get_jd_vcp_data()



if __name__ == "__main__":
    fetcher = fetcher_jd_vcp_transaction()
    fetcher.main()
