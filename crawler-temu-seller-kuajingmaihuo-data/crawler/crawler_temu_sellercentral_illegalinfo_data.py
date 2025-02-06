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
from crawler.crawler_temu_sellercentral_illegalinfo_detail import CrawlerTemuCentralIllegaliDetail
from db_model import ods_cd_sl_temu_seller_illegalidata_i_d_db_table, ods_cd_sl_temu_seller_illegalidata_i_d_field_list
from settings import illegalidata
from login.temu_login import AuthTemuLogin


class CrawlerTemuCentralIllegaliData(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.data_list = []
        self.seller_temp_cookies = {}
        self.mallId = ''
        self.mallName = ''

    @RetryDecorator.retry(max_attempts=3)
    def get_listillegalidata(self, pageNo: int = 1):
        """
        temu-跨境卖家中心-店铺管理-违规信息
        """
        headers = {
            'authority': 'agentseller.temu.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'mallid': self.mallId,  # ZHU HE SHOP: 634418216118770
            'origin': 'https://agentseller.temu.com',
            'pragma': 'no-cache',
            'referer': 'https://agentseller.temu.com/mmsos/mall-appeal.html?targetType=1',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-document-referer': 'https://agentseller.temu.com/main/authentication?redirectUrl=https%3A%2F%2Fagentseller.temu.com%2Fmmsos%2Fmall-appeal.html%3FtargetType%3D1',
        }

        json_data = {
            'targetType': 1,
            'pageNo': pageNo,
            'pageSize': 50,
        }

        response = requests.post(
            'https://agentseller.temu.com/reaper/violation/appeal/queryMallAppeals',
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

    def fetch_all_pages(self, account):
        """
        获取所有页面的数据
        """
        page_ct = 1
        has_more = True
        while has_more:
            ret_data = self.get_listillegalidata(page_ct)
            if ret_data['result']['pageData'] is None:
                break
            total = ret_data['result']['total']
            data_list = ret_data['result']['pageData']
            page_total_ct = (total - 1) // 50 + 1
            self.etl_data(account, data_list)
            has_more = page_ct < page_total_ct
            page_ct += 1
            time.sleep(random.choice([0.5, 0.8]))

    def etl_data(self, account, data_list: list):
        """
        处理数据
        :param data_list:
        :param account:
        :return:
        """
        for item in data_list:
            dt = CrawlerBase().date_str(item['informTime'])
            violationType = illegalidata['violationType'][str(item['violationType'])]
            if item['exceptionTypeList']:
                exceptionTypeList = illegalidata['exceptionTypeList'][str(item['exceptionTypeList'][0])]
            else:
                exceptionTypeList = None
            appealProgress = illegalidata['appealProgress'][str(item['appealProgress'])]
            row_dict = {
                "dt": dt,
                "violationAppealSn": item['violationAppealSn'],
                "violationType": violationType,
                "exceptionTypeList": exceptionTypeList,
                "subTargetCount": item['mallAttribute']['subTargetCount'],
                "exceptedAmount": item['mallAttribute']['exceptedAmount'],
                "actualAmount": item['mallAttribute']['actualAmount'],
                "informTime": item['informTime'],
                "lastAppealTime": item['lastAppealTime'],
                "appealProgress": appealProgress,
                "username": account,
                "mallId": self.mallId,
                "mallName": self.mallName,
            }
            self.data_list.append(row_dict)

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
        # if account == '18030068518':
        # 执行某些操作之间引入随机的延迟，以模拟人类行为或减轻对服务器的压力。choice:元素;choices:列表;
        time.sleep(random.choice([0.5, 1]))
        # self.init_user_cookies(RedisKeys.TEMU_LOGIN_KEY.value, account)
        UserInfo = self.userInfo()  # mallId和mallName信息
        mall_info_list = CrawlerBase().mallId(UserInfo)
        for userinfo in mall_info_list:
            self.mallId = str(userinfo['mallId'])
            self.mallName = userinfo['mallName']
            verify_code = self.get_code(self.cookies)
            self.seller_temp_cookies = self.loginByCode(verify_code)
            self.fetch_all_pages(account)
            self.save_to_tidb(ods_cd_sl_temu_seller_illegalidata_i_d_db_table,
                              ods_cd_sl_temu_seller_illegalidata_i_d_field_list, self.data_list)
            logger.info(
                f'temu-跨境卖家中心-店铺管理-违规信息 {account} {self.mallName} {len(self.data_list)} 采集完成')
            self.data_list.clear()  # 清空列表 list
            violationdetail = CrawlerTemuCentralIllegaliDetail(self.seller_temp_cookies, self.mallId, self.mallName)
            violationdetail.main()


    def main(self):
        user_infos = self.tidb.get_user_info('TEMU')
        for temu_info in user_infos:
            account = temu_info['account']
            password = temu_info['password']
            self.run(account, password)



if __name__ == "__main__":
    crawler = CrawlerTemuCentralIllegaliData()
    crawler.main()
