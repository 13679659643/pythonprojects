# -*- coding: utf-8 -*-
# @Time    : 2024/12/13 15:12
# @Author  : Night
# @File    : crawler-qn-promotion-amt-data.py
# @Description:
import json
import requests
from base.crawler_base import CrawlerBase
from qianniu.db_model import ods_cd_sl_qn_promotion_amt_data_i_d_db_table, \
    ods_cd_sl_qn_promotion_amt_data_i_d_field_list
from settings import RedisKeys
from loguru import logger


class CrawlerQnPromotionAmtData(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.data_list = []
        self.loginPointId = ""
        self.accessInfo = ""

    def etl_data(self, account, data_list: list):
        """
        处理数据
        :param data:
        :return:
        """
        for row in data_list:
            row['account'] = account
            row['dt'] = row['transTime'].replace('-', '')  # 交易日期
            row['amount'] = row['amount'] / 100  # 操作金额
            row['balance'] = row['balance'] / 100  # 操作后金额
            self.data_list.append(row)

    def checkAccess(self):
        """
        获取登录唯一设备id
        """
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://one.alimama.com',
            'priority': 'u=1, i',
            'referer': 'https://one.alimama.com/index.html?spm=a21dvs.28490323.c2e3fbb16.d8c4edb4d.2b023606NoQMG6',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        params = {
            'bizCode': 'universalBP',
        }

        json_data = {
            'bizCode': 'universalBP',
        }

        response = requests.post(
            'https://one.alimama.com/member/checkAccess.json',
            params=params,
            cookies=self.cookies,
            headers=headers,
            json=json_data,
        )
        ret_data = response.json()['data']
        self.loginPointId = ret_data['loginPointId']
        self.accessInfo = ret_data['accessInfo']['csrfId']

    def get_listAccountJournalWithTrans(self, offset: int = 0):
        """
        推广账户明细金额
        """
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'https://one.alimama.com',
            'priority': 'u=1, i',
            'referer': 'https://one.alimama.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }
        params = {
            'csrfId': self.accessInfo,
            'bizCode': 'universalBP',
            'offset': str(offset),
            'beginTime': self.start_time,
            'endTime': self.end_time,
            'timeType': 'trans',
            'limit': '40',
            'loginPointId': self.loginPointId,
        }
        response = requests.get(
            'https://stlacct.alimama.com/settleAccount/account/listAccountJournalWithTrans.json',
            params=params,
            cookies=self.cookies,
            headers=headers,
        )
        if response.status_code == 200:
            return response.json()
        return None

    def fetch_all_pages(self, account):
        """
        获取所有页面的数据
        """
        page_ct = 0
        has_more = True
        while has_more:
            ret_data = self.get_listAccountJournalWithTrans(page_ct * 40)
            if ret_data is None:
                break
            total = ret_data['data']['total']
            data_list = ret_data['data']['list']
            page_total_ct = (total - 1) // 40 + 1
            self.etl_data(account, data_list)
            has_more = page_ct < (page_total_ct - 1)
            page_ct += 1

    def main(self):
        user_infos = self.tidb.get_user_info('TB')
        for dw_info in user_infos:
            account = dw_info['account']
            self.init_user_cookies(RedisKeys.TB_MYSELLER_LOGIN_KEY.value, account)
            self.checkAccess()
            self.start_time, self.end_time = self.get_time_range(in_day=7)
            self.fetch_all_pages(account)
            self.save_to_tidb(ods_cd_sl_qn_promotion_amt_data_i_d_db_table,
                              ods_cd_sl_qn_promotion_amt_data_i_d_field_list, self.data_list)
            logger.info(f'千牛-推广中心-账户明细 {account} {len(self.data_list)} 采集完成')
            self.data_list.clear()


if __name__ == "__main__":
    crawler = CrawlerQnPromotionAmtData()
    crawler.main()
