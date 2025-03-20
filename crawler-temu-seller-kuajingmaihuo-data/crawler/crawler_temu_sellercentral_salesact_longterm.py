# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import random
import time

import requests
from loguru import logger
from base.crawler_base import CrawlerBase, RetryDecorator
from data_pipeline.mongo_tidb_transfer_salesact_long import MongoTidbTransferLong
from db_model import ods_cd_sl_temu_seller_salesactlong_i_d_db_table, ods_cd_sl_temu_seller_salesactlong_i_d_field_list
from settings import db_name, mg_salesactlong_field_list, salesactlong_table_name
from login.temu_login import AuthTemuLogin


class CrawlerTemuCentralSalesActLong(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.data_list = []
        self.mallId = ''
        self.mallName = ''
        self.table_ob=self.mongo_ob.load_table_ob(db_name, salesactlong_table_name)
        # self.now_date = datetime.now()
        # self.startDate = (self.now_date - timedelta(days=31)).strftime('%Y-%m-%d 00:00:00')
        # self.endDate = self.now_date.strftime('%Y-%m-%d 23:59:59')

    @RetryDecorator.retry(max_attempts=3)
    def get_productlist(self, pageNo: int = 1):
        """
        temu-跨境卖家中心-店铺营销-营销活动-长期活动
        """
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'anti-content': '0aqAfa5e-wCEsSIAPIqBOQwEiUXfRTAHwbMA7NC-Rgn38-zrY43ZAYx_rr2DPDfDXuebCQK5zxIzuE03duHQ_qLCWTHiIWXbJ6Y2WeLq9R9u9h6lAD8T6Syaa6-rY03gXmAbhb0jTqMl6EoqoW_sqZjXkN6YVmbO5286mb-cXtaC7U-UGLfHefb2e2RoGBPATATWHdaZrUgUQL6Xe6b2K4AaOMXr9fPIRQNqQT0_lr5WX7dm__DJT5Mg3EeTQSEbol-Od032luuKVyCRCLp4p2iZRUB-GLlOQfSnCQPKoR2iBUCWwqSEYdTSRnJnCQDRTbw4JAXUKt4EZOirAGdMfqdPI8HYH_HqGqY8XpX5nfNhApN7Q8gbfGXHHx__h8matGHy2tCK4bmt4mrMABhHn91VokwMyoAmUkBFSD-b-EBb1kBF1DBs1k3VcDBeHEBscEBeVDBsCgn0VBllYorfve-vVExvOp3bFuFbcTU3Kh1B_VSVBW-KA_7sxhJV_CEBcCez4H92maXI2d1qgoYswoG4Mf_oylph0nGigjnqWzXqwTYh0y4W6yYs6PxHyXv8slpHrXyseoqZhfqdrdn5T8y0g2TPpCaGDgSg3Dsn_duPuACgvBTzbVM-F3evb4DFvAEgKMM62r-sl27vf1_FyH_EffdBw9dDfKkgOV2OXSfVCT0HqZyK4TMvDNJHxwvsxZmOY04lpWGINTSaporGqYr1OoKctC1jnNa8uejKuTjaZMl7ylJGq999nlB9T-v_5l5r',
            'cache-control': 'max-age=0',
            'content-type': 'application/json',
            'mallid': self.mallId,
            'origin': 'https://seller.kuajingmaihuo.com',
            'priority': 'u=1, i',
            'referer': 'https://seller.kuajingmaihuo.com/activity/marketing-activity/log',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        }

        json_data = {
            'pageNo': pageNo,
            'pageSize': 50,
            # 'sessionStartTimeFrom': CrawlerBase().timestamp(self.startDate),
            # 'sessionEndTimeTo': CrawlerBase().timestamp(self.endDate),
        }

        response = requests.post(
            'https://seller.kuajingmaihuo.com/marvel-mms/cn/api/kiana/gambit/marketing/enroll/list',
            cookies=self.cookies,
            headers=headers,
            json=json_data,
        )
        if response.json()['result'] is None:
            logger.info(response.json())
            return None
        if response.status_code == 200:
            return response.json()
        return None

    def fetch_all_pages(self,):
        """
        获取所有页面的数据
        """
        page_ct = 1
        has_more = True
        while has_more:
            ret_data = self.get_productlist(page_ct)
            if ret_data['result']['list'] is None:
                break
            total = ret_data['result']['total']
            data_list = ret_data['result']['list']
            result = CrawlerBase().add_fields(data_list, 'mallId', self.mallId, 'mallName', self.mallName)
            page_total_ct = (total - 1) // 50 + 1
            self.data_list.extend(result)
            has_more = page_ct < page_total_ct
            page_ct += 1
            time.sleep(random.choice([3.2, 2.5]))  # 可选：添加延迟避免频繁请求

    @RetryDecorator.retry_decorator()
    def run(self, account: str, password: str):
        """
        流程主体
        :return:
        """
        temulogin = AuthTemuLogin(account, password)
        self.cookies = temulogin.main()
        if not self.cookies:
            return
        UserInfo = self.userInfo()
        mall_info_list = CrawlerBase().mallId(UserInfo)
        for userinfo in mall_info_list:
            self.data_list.clear()  # 清空列表 list
            self.mallId = str(userinfo['mallId'])
            self.mallName = userinfo['mallName']
            self.fetch_all_pages()
            self.mongo_ob.bulk_save_data(self.data_list, mg_salesactlong_field_list, self.table_ob)
            logger.info(
                f'temu-跨境卖家中心-店铺营销-营销活动-长期活动 {account} {self.mallName} {len(self.data_list)} 存入mongo完成')


    def main(self):
        user_infos = self.tidb.get_user_info('TEMU')
        for temu_info in user_infos:
            account = temu_info['account']
            # if account == '13074832078':
            password = temu_info['password']
            self.run(account, password)
        salesactlong_list = MongoTidbTransferLong().etl_data()
        self.save_to_tidb(ods_cd_sl_temu_seller_salesactlong_i_d_db_table,
                          ods_cd_sl_temu_seller_salesactlong_i_d_field_list, salesactlong_list)
        logger.info(f'temu-跨境卖家中心-店铺营销-营销活动-长期活动 {len(salesactlong_list)} 条数据采集完成')



if __name__ == "__main__":
    crawler = CrawlerTemuCentralSalesActLong()
    crawler.main()
