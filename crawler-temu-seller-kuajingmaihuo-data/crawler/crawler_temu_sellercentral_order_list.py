# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import random
import time
from datetime import datetime, timedelta
import requests
from loguru import logger
from base.crawler_base import CrawlerBase, RetryDecorator
from data_pipeline.mongo_tidb_transfer_orderlist import MongoTidbTransferOrderList
from digiCore.db.tidb.core import TiDBDao

from db_model import ods_cd_sl_temu_seller_orderlist_i_d_db_table, ods_cd_sl_temu_seller_orderlist_i_d_field_list
from settings import db_name, mg_orderlist_field_list, orderlist_table_name
from login.temu_login import AuthTemuLogin


class CrawlerTemuCentralOrderList(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.order_list = []
        self.mallId = ''
        self.mallName = ''
        self.table_ob=self.mongo_ob.load_table_ob(db_name, orderlist_table_name)
        self.seller_temp_cookies = ''
        self.tidb_ob = TiDBDao()
        self.now_date = datetime.now()
        self.startDate = (self.now_date - timedelta(days=31)).strftime('%Y-%m-%d 00:00:00')
        self.endDate = self.now_date.strftime('%Y-%m-%d 23:59:59')

    @RetryDecorator.retry(max_attempts=3)
    def get_productlist(self, pageNo: int = 1):
        """
        temu-跨境卖家中心-订单管理-订单列表-买家履约订单
        """
        headers = {
            'authority': 'agentseller.temu.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'mallid': self.mallId,
            'origin': 'https://agentseller.temu.com',
            'pragma': 'no-cache',
            'referer': 'https://agentseller.temu.com/mmsos/orders.html?fulfillmentMode=0&queryType=0&sortType=1&timeZone=UTC%2B8&needBuySignService=0&sellerNoteLabelList=&packageAbnormalTypeList=',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-document-referer': 'https://agentseller.temu.com/mmsos/mall-appeal.html?numberList=240919004799423907&numberType=1&targetType=1',
            'x-phan-data': '0aeJx7xMxiYPiI2Sra0NzY3NTI3MDQ3MjEVAfGM7Y0M7KMBQCubQie',
        }

        json_data = {
            'fulfillmentMode': 0,
            'pageNumber': pageNo,
            'pageSize': 100,
            'queryType': 0,
            'sortType': 1,
            'parentOrderTimeStart': int(CrawlerBase.timestamp(self.startDate)/1000),
            'parentOrderTimeEnd': int(CrawlerBase.timestamp(self.endDate)/1000),
            'timeZone': 'UTC+8',
            'parentAfterSalesTag': 0,
            'sellerNoteLabelList': [],
        }

        response = requests.post(
            'https://agentseller.temu.com/kirogi/bg/mms/recentOrderList',
            cookies=self.seller_temp_cookies,
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
            if ret_data['result']['pageItems'] is None:
                break
            total = ret_data['result']['totalItemNum']
            order_list = ret_data['result']['pageItems']
            for item in order_list:
                item['mallId'] = self.mallId
                item['mallName'] = self.mallName
                item['parentOrderSn'] = item['parentOrderMap']['parentOrderSn']
                item['dt'] = CrawlerBase.date_str(item['parentOrderMap']['parentOrderTimeStr'])  # 创建时间yyyyMMdd
            page_total_ct = (total - 1) // 100 + 1
            self.order_list.extend(order_list)
            has_more = page_ct < page_total_ct
            page_ct += 1

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
        time.sleep(random.choice([0.5, 1]))
        UserInfo = self.userInfo()
        mall_info_list = CrawlerBase().mallId(UserInfo)
        for userinfo in mall_info_list:
            self.mallId = str(userinfo['mallId'])
            self.mallName = userinfo['mallName']
            verify_code = self.get_code(self.cookies)
            self.seller_temp_cookies = self.loginByCode(verify_code)
            self.order_list.clear()  # 清空列表 list 放在此处避免重试时累计值
            self.fetch_all_pages()
            self.mongo_ob.bulk_save_data(self.order_list, mg_orderlist_field_list, self.table_ob)
            logger.info(
                f'temu-跨境卖家中心-订单管理-订单列表-买家履约订单 {account} {self.mallName} {len(self.order_list)} 存入mongo完成')


    def main(self):
        user_infos = self.tidb.get_user_info('TEMU')
        for temu_info in user_infos:
            account = temu_info['account']
            # if account == '13074832078':
            password = temu_info['password']
            self.run(account, password)
        etl_order_list = MongoTidbTransferOrderList().etl_order_list()
        self.save_to_tidb(ods_cd_sl_temu_seller_orderlist_i_d_db_table,
                          ods_cd_sl_temu_seller_orderlist_i_d_field_list, etl_order_list)
        logger.info(f'temu-跨境卖家中心-订单管理-订单列表-买家履约订单 {len(etl_order_list)} 条数据采集完成')



if __name__ == "__main__":
    crawler = CrawlerTemuCentralOrderList()
    crawler.main()
