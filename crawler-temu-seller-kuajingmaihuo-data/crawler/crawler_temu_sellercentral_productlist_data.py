# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:

import requests
from loguru import logger
from base.crawler_base import CrawlerBase, RetryDecorator
from data_pipeline.mongo_tidb_transfer_product import MongoTidbTransfer
from db_model import dim_cd_sl_temu_seller_productlist_i_d_db_table, dim_cd_sl_temu_seller_productlist_i_d_field_list, \
    dim_cd_sl_temu_seller_productlist_details_i_d_db_table, dim_cd_sl_temu_seller_productlist_details_i_d_field_list
from settings import mg_product_list_field_list, db_name, table_name
from login.temu_login import AuthTemuLogin


class CrawlerTemuCentralProductList(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.data_list = []
        self.mallId = ''
        self.mallName = ''
        self.table_ob=self.mongo_ob.load_table_ob(db_name, table_name)

    @RetryDecorator.retry(max_attempts=3)
    def get_productlist(self, pageNo: int = 1):
        """
        temu-跨境卖家中心-商品管理-商品列表
        """
        headers = {
            'authority': 'seller.kuajingmaihuo.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'mallid': self.mallId,
            'origin': 'https://seller.kuajingmaihuo.com',
            'pragma': 'no-cache',
            'referer': 'https://seller.kuajingmaihuo.com/goods/product/list',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }

        json_data = {
            'page': pageNo,
            'pageSize': 50,
        }

        response = requests.post(
            'https://seller.kuajingmaihuo.com/bg-visage-mms/product/skc/pageQuery',
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
            try:
                if ret_data['result']['pageItems'] is None:
                    break
            except Exception as e:
                logger.info(ret_data)
                pass
            total = ret_data['result']['total']
            data_list = ret_data['result']['pageItems']
            page_total_ct = (total - 1) // 50 + 1
            self.data_list.extend(data_list)
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
        UserInfo = self.userInfo()
        mall_info_list = CrawlerBase().mallId(UserInfo)
        for userinfo in mall_info_list:
            self.mallId = str(userinfo['mallId'])
            self.mallName = userinfo['mallName']
            self.fetch_all_pages()
            self.mongo_ob.bulk_save_data(self.data_list, mg_product_list_field_list, self.table_ob)
            logger.info(
                f'temu-跨境卖家中心-商品管理-商品列表 {account} {self.mallName} {len(self.data_list)} 存入mongo完成')
            self.data_list.clear()  # 清空列表 list


    def main(self):
        user_infos = self.tidb.get_user_info('TEMU')
        for temu_info in user_infos:
            account = temu_info['account']
            # if account == '18650441312':
            password = temu_info['password']
            self.run(account, password)
        product_list = MongoTidbTransfer().etl_data()
        self.save_to_tidb(dim_cd_sl_temu_seller_productlist_i_d_db_table,
                          dim_cd_sl_temu_seller_productlist_i_d_field_list, product_list)
        logger.info(f'temu-跨境卖家中心-商品管理-商品列表 {len(product_list)} 条数据采集完成')
        product_details_list = MongoTidbTransfer().etl_Details_data()
        self.save_to_tidb(dim_cd_sl_temu_seller_productlist_details_i_d_db_table,
                          dim_cd_sl_temu_seller_productlist_details_i_d_field_list, product_details_list)
        logger.info(f'temu-跨境卖家中心-商品管理-商品列表明细数据 {len(product_details_list)} 条数据采集完成')



if __name__ == "__main__":
    crawler = CrawlerTemuCentralProductList()
    crawler.main()
