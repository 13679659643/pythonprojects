# -*- coding: utf-8 -*-
# @Time    : 2025/1/8 9:24
# @Author  : Night
# @File    : crawler_yabao_drop_order_overseas_warehouse.py
# @Description:
import json
from datetime import datetime, timedelta

import requests
from loguru import logger

from crawler_base import BaseCrawler
from db_model import ods_scg_wld_yabao_dropshipping_order_table, ods_scg_wld_yabao_dropshipping_order_i_d_field_list
from method import RetryDecorator
from settings import fetcher_info
import ddddocr
import base64
from io import BytesIO
from PIL import Image


class CrawlerYapaoOverseasWarehouse(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.session = requests.session()
        self.now_date = datetime.now()
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.start_date = (self.now_date - timedelta(days=90)).strftime('%Y-%m-%d')
        self.data_list = []

    def init_logistic(self, logistics_provider: str):
        self.logistics_provider = fetcher_info[logistics_provider]['logistics_provider']
        self.logistics_provider_code = logistics_provider
        self.HASH_AUTH_TOKEN = fetcher_info[logistics_provider]['hash_token_path']
        self.key = fetcher_info[logistics_provider]['token_key']

    @RetryDecorator.retry(max_attempts=15)
    def get_captcha_img(self):
        """
        字母验证码识别
        :return:
        """
        code_url = 'http://47.106.234.129:808/Login/GetCaptcha'
        data = {
            'codeType': '1',
        }

        response = self.session.post(code_url,
                                     data=data, verify=False)
        if response.status_code == 200:
            jsonp_data = response.json()
            base64_data = jsonp_data['img']
            img_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(img_data))
            image.save('yb_code.png')
            uuid = jsonp_data['uuid']
            ocr = ddddocr.DdddOcr(beta=True, show_ad=False)
            with open("yb_code.png", "rb") as image_file:
                image = image_file.read()
            img_expression = ocr.classification(image)
            return uuid, img_expression
        return None

    def get_order_list_new(self, page: int = 1):
        """
        :param page: 页数
        :return:
        """
        CreateTime = f"{self.start_date} 00:00:00 ~ {self.end_date} 23:59:59"
        params = {
            'page': str(page),
            'limit': '200',
            'Style': '1',
            'Status': '4',
            'CreateTime': CreateTime,
            'selsearchno': '1',
            'NoVal': '',
            'ChannelInfoID': '',
            'CountryID': '',
            'StockID': '',
            'MarkColor': '',
            'DeliveryTime': '',
            'SKU': '',
            'BatchNo': '',
        }

        response = self.session.get(
            'http://47.106.234.129:808/Home/GetOrderListNew',
            params=params,
            verify=False,
        )
        if response.status_code == 200:
            return response.json()
        return None

    def etl_data(self, dataList):
        """
        列表数据
        :param dataList:
        :return:
        """
        for row in dataList:
            row['dt'] = row['CreateTime'].split(" ")[0].replace("-", "")
            self.data_list.append(row)

    def fetch_all_pages(self):
        """
        获取所有页面的数据
        """
        pageNo = 1
        while True:
            ret_data = self.get_order_list_new(pageNo)
            if not ret_data:
                break
            dataList = ret_data['data']
            total = ret_data['count']
            page_total_ct = (total - 1) // 200 + 1
            self.etl_data(dataList)
            if pageNo >= page_total_ct:
                break
            pageNo += 1

    @RetryDecorator.retry(max_attempts=15)
    def web_login(self):
        with self.redis_client.conn as redis_conn:
            if not redis_conn.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                uuid_and_code = self.get_captcha_img()
                if uuid_and_code:
                    uuid, code = uuid_and_code
                    data = {
                        'username': self.config[self.logistics_provider_code]['username'],
                        'password': self.config[self.logistics_provider_code]['password'],
                        'remember': '0',
                        'uuid': uuid,
                        'captcha': code,
                    }
                    cookies = {
                        'lang': 'zh-CN',
                    }
                    response = self.session.post('http://47.106.234.129:808/Login/WebCheckLogin/', cookies=cookies,
                                                 data=data, verify=False)
                    if response.json()['msg'] != '验证码错误!':
                        set_cookies = dict(response.cookies)
                        redis_conn.hset(self.HASH_AUTH_TOKEN, self.key, json.dumps(set_cookies))
                        redis_conn.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 2 * 60 * 60, "1")
                        logger.info("亚豹海外仓-登录账号成功")
                    else:
                        logger.warning(f"登录请求失败，状态码：{response.status_code}")
                else:
                    logger.info("亚豹海外仓-获取验证码失败，重新获取验证码")

            return redis_conn.hget(self.HASH_AUTH_TOKEN, self.key)

    def init_headers(self, cookies):
        """
        更新账号登录cookie
        :param cookies:
        :return:
        """
        cookie_dict = json.loads(cookies.decode())
        self.session.cookies.update(cookie_dict)

    def insert_to_tidb(self):
        """
        存入到数据库中
        :return:
        """
        self.tidb.insert_data(ods_scg_wld_yabao_dropshipping_order_table,
                              ods_scg_wld_yabao_dropshipping_order_i_d_field_list,
                              self.data_list)
        logger.info(f'亚豹海外仓-出库数据同步{len(self.data_list)}完成')

    def main(self):
        self.init_logistic('YABAO')
        yb_cookies = self.web_login()
        if not yb_cookies:
            return
        self.init_headers(yb_cookies)
        self.fetch_all_pages()
        self.insert_to_tidb()


if __name__ == '__main__':
    CrawlerYapaoOverseasWarehouse().main()
