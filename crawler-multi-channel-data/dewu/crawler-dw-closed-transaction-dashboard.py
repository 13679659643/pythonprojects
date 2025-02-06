# -*- coding: utf-8 -*-
# @Time    : 2024/12/10 16:09
# @Author  : Night
# @File    : crawler-dw-closed-transaction-dashboard.py
# @Description:
import execjs
import requests
from base.crawler_base import CrawlerBase
from dewu import get_file_path
from dewu.db_model import ods_cd_sl_dw_closed_transaction_dashboard_db_table, \
    ods_cd_sl_dw_closed_transaction_dashboard_i_d_field_list
from settings import RedisKeys
from loguru import logger
from decimal import Decimal, getcontext


class CrawlerDwClosedTransactionDashboard(CrawlerBase):
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
        getcontext().prec = 4
        cancelAmount = data['cancelAmount']['value'] / 100  # 取消单金额
        cancelOrderCnt = data['cancelOrderCnt']['value']  # 取消单量
        cancelRate = Decimal(data['cancelRate']['value']) / Decimal(10000)  # 订单取消占比
        returnAmount = data['returnAmount']['value'] / 100  # 退货订单金额
        returnOrderCnt = data['returnOrderCnt']['value']  # 退货单量
        returnRate = Decimal(data['returnRate']['value']) / Decimal(10000)  # 退货订单占比
        unpaidAmount = data['unpaidAmount']['value'] / 100  # 未支付单金额
        unpaidOrderCnt = data['unpaidOrderCnt']['value']  # 未支付单量
        unpaidRate = Decimal(data['unpaidRate']['value']) / Decimal(10000)  # 未支付订单占比
        unperformanceAmount = data['unperformanceAmount']['value'] / 100  # 未履约订单金额
        unperformanceOrderCnt = data['unperformanceOrderCnt']['value']  # 未履约单量
        unperformanceRate = Decimal(data['unperformanceRate']['value']) / Decimal(10000)  # 未履约订单占比
        item = {
            'cancelAmount': cancelAmount,
            'cancelOrderCnt': cancelOrderCnt,
            'cancelRate': cancelRate,
            'returnAmount': returnAmount,
            'returnOrderCnt': returnOrderCnt,
            'returnRate': returnRate,
            'unpaidAmount': unpaidAmount,
            'unpaidOrderCnt': unpaidOrderCnt,
            'unpaidRate': unpaidRate,
            'unperformanceAmount': unperformanceAmount,
            'unperformanceOrderCnt': unperformanceOrderCnt,
            'unperformanceRate': unperformanceRate
        }
        return item

    def get_datacenter_trade_close(self, account, sdate):
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
                'timeType': 7,
                'startTime': date_time_sft,
                'endTime': date_time_sft,
            },
        }
        json_data['sign'] = self.get_sign(json_data)
        response = requests.post(
            'https://stark.dewu.com/api/v1/h5/biz/data-operation/template/v2/queryByTemplate/datacenter_trade_close',
            cookies=self.sensor_cookies,
            headers=headers,
            json=json_data,
            timeout=15
        )
        if response.status_code != 200:
            logger.info(f'得物-交易分析-交易关闭 {date_time_sft} 采集失败')
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
            for sdate in self.generate_date_list(in_day=31):
                self.get_datacenter_trade_close(account, sdate)
            self.save_to_tidb(ods_cd_sl_dw_closed_transaction_dashboard_db_table,
                              ods_cd_sl_dw_closed_transaction_dashboard_i_d_field_list, self.data_list)
            logger.info(f'得物-交易分析-交易关闭 {account} {len(self.data_list)} 采集完成')
            self.data_list.clear()


if __name__ == "__main__":
    crawler = CrawlerDwClosedTransactionDashboard()
    crawler.main()
