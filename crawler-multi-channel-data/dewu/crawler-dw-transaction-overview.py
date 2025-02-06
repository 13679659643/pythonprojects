# -*- coding: utf-8 -*-
# @Time    : 2024/12/11 10:35
# @Author  : Night
# @File    : crawler-dw-transaction-overview.py
# @Description:
import execjs
import requests
from base.crawler_base import CrawlerBase
from dewu import get_file_path
from dewu.db_model import ods_cd_sl_dw_transaction_overview_db_table, \
    ods_cd_sl_dw_transaction_overview_i_d_field_list
from settings import RedisKeys
from loguru import logger


class CrawlerDwTransactionOverview(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.sensor_cookies = {
            'sensorsdata2015jssdkcross': '',
        }
        self.data_list = []

    def get_sign(self, params):
        """
        加密sign
        """
        with open(get_file_path('sign.js'), 'r', encoding='utf-8') as fp:
            jsdata = fp.read()
        ctx = execjs.compile(jsdata)
        sign = ctx.call('biz_sign', params)
        return sign

    def etl_data(self, data: dict):
        """
        处理数据
        :param data:
        :return:
        """
        onlyPrdAccessUv = data['onlyPrdAccessUv']['value']  # 商详访客数
        paidAmount = data['paidAmount']['value'] / 100  # 支付金额
        paidAvePricePerOrder = data['paidAvePricePerOrder']['value'] / 100  # 支付笔单价
        paidBuyerCnt = data['paidBuyerCnt']['value']  # 支付客户数
        paidOrderCnt = data['paidOrderCnt']['value']  # 支付单量
        submitAmount = data['submitAmount']['value'] / 100  # 提交订单金额
        submitBuyerCnt = data['submitBuyerCnt']['value']  # 提交订单客户数
        submitOrderCnt = data['submitOrderCnt']['value']  # 提交订单数
        successAmount = data['successAmount']['value'] / 100  # 交易成功金额
        successAvePricePerOrder = data['successAvePricePerOrder']['value'] / 100  # 交易成功笔单价
        successOrderCnt = data['successOrderCnt']['value']  # 交易成功单量
        item = {
            'onlyPrdAccessUv': onlyPrdAccessUv,
            'paidAmount': paidAmount,
            'paidAvePricePerOrder': paidAvePricePerOrder,
            'paidBuyerCnt': paidBuyerCnt,
            'paidOrderCnt': paidOrderCnt,
            'submitAmount': submitAmount,
            'submitBuyerCnt': submitBuyerCnt,
            'submitOrderCnt': submitOrderCnt,
            'successAmount': successAmount,
            'successAvePricePerOrder': successAvePricePerOrder,
            'successOrderCnt': successOrderCnt,
        }
        return item

    def get_datacenter_trade_outline(self, account, sdate):
        """
        :param account: 用户
        :param sdate: 日期范围
        :return:
        """
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'appid': 'h5',
            'cache-control': 'no-cache',
            'channel': 'pc',
            'clientid': 'stark',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://stark.dewu.com',
            'passporttoken': self.cookies,
            'platform': 'h5',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://stark.dewu.com/main/dataCenter/newtTransactionData',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'syscode': 'DEWU_MERCHANT_PLATFORM_DU_USER_T',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        }
        date_time_sft = sdate.replace("-", "")
        json_data = {
            'params': {
                'amountType': 2,
                'timeType': 7,
                'startTime': date_time_sft,
                'endTime': date_time_sft,
            },
        }
        json_data['sign'] = self.get_sign(json_data)
        response = requests.post(
            'https://stark.dewu.com/api/v1/h5/biz/data-operation/template/v2/queryByTemplate/datacenter_trade_outline',
            cookies=self.sensor_cookies,
            headers=headers,
            json=json_data,
            timeout=15
        )
        if response.status_code != 200:
            logger.info(f'得物-交易分析-交易概览 {date_time_sft} 采集失败')
            return
        ret_data = response.json()['data']
        if not ret_data:
            return
        new_data = self.etl_data(ret_data)
        new_data['account'] = account
        new_data['dt'] = date_time_sft
        self.data_list.append(new_data)

    def main(self):
        user_infos = self.tidb.get_user_info('DW')
        for dw_info in user_infos:
            account = dw_info['account']
            self.init_user_cookies(RedisKeys.DW_STARK_LOGIN_KEY.value, account)
            for sdate in self.generate_date_list(in_day=7):
                self.get_datacenter_trade_outline(account, sdate)
            self.save_to_tidb(ods_cd_sl_dw_transaction_overview_db_table,
                              ods_cd_sl_dw_transaction_overview_i_d_field_list, self.data_list)
            logger.info(f'得物-交易分析-交易概览 {account} {len(self.data_list)} 采集完成')
            self.data_list.clear()


if __name__ == "__main__":
    crawler = CrawlerDwTransactionOverview()
    crawler.main()
