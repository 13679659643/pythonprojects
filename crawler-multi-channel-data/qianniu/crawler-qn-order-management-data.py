# -*- coding: utf-8 -*-
# @Time    : 2024/12/25 10:53
# @Author  : Night
# @File    : crawler-qn-order-management-data.py
# @Description:
import random
import time
from datetime import datetime
import requests
from base.crawler_base import CrawlerBase
from qianniu.db_model import ods_cd_sl_qn_order_management_data_i_d_db_table, \
    ods_cd_sl_qn_order_management_data_i_d_field_list
from settings import RedisKeys
from loguru import logger


class CrawlerQnOrderManagementData(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.data_list = []

    def etl_data(self, account, sdate, data_list: list):
        """
        :param account 账号
        :param sdate 付款日期
        :param 列表
        """
        for data in data_list:
            data_dict = {}
            data_dict['dt'] = sdate.replace('-', '')
            data_dict['account'] = account
            data_dict['id'] = data['id']
            data_dict['currency'] = data['extra']['currency']  # 币种
            data_dict['actualFee'] = data['payInfo']['actualFee']  # 实收款
            data_dict['postType'] = data['payInfo']['postType']  # 含快递
            data_dict['text'] = data['statusInfo']['text']  # 交易状态
            data_dict['quantity'] = data['subOrders'][0]['quantity']  # 数量
            data_dict['realTotal'] = data['subOrders'][0]['priceInfo']['realTotal']  # 单价
            self.data_list.append(data_dict)

    def get_order_list(self, sdate, page: int = 1):
        """
        :param sdate 付款日期
        :param page 页数
        """

        date_format = '%Y-%m-%d'

        # 将日期字符串转换为 datetime 对象
        date_object = datetime.strptime(sdate, date_format)

        # 获取当天的开始时间 (00:00:00)
        start_of_day = date_object.replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取当天的结束时间 (23:59:59)
        end_of_day = date_object.replace(hour=23, minute=59, second=59, microsecond=0)

        # 将 datetime 对象转换为时间戳（秒级）
        timestamp_start_seconds = start_of_day.timestamp()
        timestamp_end_seconds = end_of_day.timestamp()

        # 将秒级时间戳转换为毫秒级时间戳（13位）
        timestamp_start_milliseconds = int(timestamp_start_seconds * 1000)
        timestamp_end_milliseconds = int(timestamp_end_seconds * 1000)
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://myseller.taobao.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://myseller.taobao.com/home.htm/trade-platform/tp/sold',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        params = {
            'event_submit_do_query': '1',
            '_input_charset': 'utf8',
        }
        data = {
            'isQnNew': 'true',
            'isHideNick': 'true',
            'prePageNo': '1',
            'sifg': '0',
            'action': 'itemlist/SoldQueryAction',
            'close': '0',
            'pageNum': str(page),  # 翻页页数
            'tabCode': 'latest3Months',
            'useCheckcode': 'false',
            'errorCheckcode': 'false',
            'payDateBegin': str(timestamp_start_milliseconds),
            'rateStatus': 'ALL',
            'buyerNick': '',
            'orderStatus': 'ALL',
            'pageSize': '15',
            'dateEnd': '0',
            'rxOldFlag': '0',
            'rxSendFlag': '0',
            'dateBegin': '0',
            'tradeTag': '0',
            'rxHasSendFlag': '0',
            'auctionType': '0',
            'sellerNick': '',
            'notifySendGoodsType': 'ALL',
            'sellerMemoFlag': 'F-5',
            'useOrderInfo': 'false',
            'logisticsService': 'ALL',
            'o2oDeliveryType': 'ALL',
            'rxAuditFlag': '0',
            'queryOrder': 'desc',
            'holdStatus': '0',
            'rxElectronicAuditFlag': '0',
            'queryMore': 'false',
            'payDateEnd': str(timestamp_end_milliseconds),
            'rxWaitSendflag': '0',
            'sellerMemo': '0',
            'queryBizType': 'ALL',
            'rxElectronicAllFlag': '0',  # 紫色旗子
            'rxSuccessflag': '0',
            'refund': 'ALL',
            'yushouStatus': 'ALL',
            'deliveryTimeType': 'ALL',
            'payMethodType': 'ALL',
            'orderType': 'ALL',
            'appName': 'ALL',
            'buyerEncodeId': '',
        }

        response = requests.post(
            'https://trade.taobao.com/trade/itemlist/asyncSold.htm',
            params=params,
            cookies=self.cookies,
            headers=headers,
            data=data,
        )
        if response.status_code == 200:
            return response.json()
        return None

    def fetch_all_pages(self, account, sdate):
        """
        获取所有页面的数据
        """
        page_ct = 1
        has_more = True
        while has_more:
            ret_data = self.get_order_list(sdate, page_ct)
            choice_time = random.choice([0.8, 1, 1.2, 1.8])  # 风控严格
            time.sleep(choice_time)
            if ret_data is None:
                break
            if ret_data.get('data', {}).get('url'):
                logger.info(f'{account} {sdate} 出现风控')
                break
            total_page = ret_data['page']['totalPage']
            data_list = ret_data['mainOrders']
            if not ret_data:
                return
            self.etl_data(account, sdate, data_list)
            has_more = page_ct < total_page
            page_ct += 1

    def main(self):
        user_infos = self.tidb.get_user_info('TB')
        for dw_info in user_infos:
            account = dw_info['account']
            self.init_user_cookies(RedisKeys.TB_MYSELLER_LOGIN_KEY.value, account)
            for sdate in self.generate_date_list(in_day=3):
                self.fetch_all_pages(account, sdate)
            self.save_to_tidb(ods_cd_sl_qn_order_management_data_i_d_db_table,
                              ods_cd_sl_qn_order_management_data_i_d_field_list, self.data_list)
            logger.info(f'千牛-交易-订单管理 {account} {len(self.data_list)} 采集完成')
            self.data_list.clear()


if __name__ == '__main__':
    crawler = CrawlerQnOrderManagementData()
    crawler.main()
