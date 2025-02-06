# -*- coding: utf-8 -*-
# @Time    : 2024/12/11 14:51
# @Author  : Night
# @File    : crawler-dw-promotion-data.py
# @Description:
import subprocess
import execjs
import requests
from base.crawler_base import CrawlerBase
from dewu import get_file_path
from dewu.db_model import ods_cd_sl_dw_ad_promotion_db_table, \
    ods_cd_sl_dw_ad_promotion_i_d_field_list
from settings import RedisKeys
from loguru import logger


class CrawlerDwPromotionData(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.sensor_cookies = {
            'sensorsdata2015jssdkcross': '',
        }
        self.data_list = []
        self.ad_accessToken = ''  # 营销token

    def run_node_script(self, script_name, *args):
        """
        :param script_name: js执行文件
        :param args: 传递参数
        :return:
        """
        result = subprocess.run(
            ["node", script_name] + list(args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return result.stdout.strip()

    def get_sign(self, params):
        """
        加密sign
        """
        with open(get_file_path('sign.js'), 'r', encoding='utf-8') as fp:
            jsdata = fp.read()
        ctx = execjs.compile(jsdata)
        sign = ctx.call('biz_sign', params)
        return sign

    def token_replace(self):
        """
        token按照板块进行更新
        :return:
        """
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://stark.dewu.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://stark.dewu.com/main/newAdv/advHome',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        }
        json_data = {
            'principal': self.cookies,
            'sysCode': 'DEWU_MERCHANT_PLATFORM_DU_USER_T',
            'channel': 'pc',
            'clientId': 'stark',
            'credentials': 'f22f35254aff49c0b032b59b55d4286b',  # 针对营销板块
        }
        json_data['sign'] = self.get_sign(json_data)

        response = requests.post(
            'https://stark.dewu.com/api/v1/h5/passport/v1/oauth2/tokenReplace',
            cookies=self.sensor_cookies,
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            self.ad_accessToken = response.json()['data']['accessToken']
            return True
        else:
            logger.error(f'获取token失败:{response.text}')
            return

    def etl_data(self, data: dict):
        """
        处理数据
        :param data:
        :return:
        """
        itemlist = data['itemList']
        consumeFee = itemlist[0]['value']  # 消耗(元)
        exposureCnt = itemlist[1]['value']  # 曝光(次)
        clickCnt = itemlist[2]['value']  # 点击(次)
        paymentOrder = itemlist[3]['value']  # 引导支付单量(单)
        paymentAmt = itemlist[4]['value']  # 引导支付金额(元)
        productRoi = itemlist[5]['value']  # 投产比ROI
        clickRate = itemlist[6]['value']  # 点击率(%)
        thousandexposureCost = itemlist[7]['value']  # 千次曝光费用(元)
        DepaymentOrderQty = itemlist[8]['value']  # 直接支付单量(单)
        DepaymentAmt = itemlist[9]['value']  # 直接支付金额(元)
        clickConversionRate = itemlist[10]['value']  # 点击转化率(%)
        orderCost = itemlist[11]['value']  # 订单成本(元)
        DeCollectOrderNumber = itemlist[12]['value']  # 直接收藏预约数(次)
        CollectOrderCost = itemlist[13]['value']  # 收藏预约成本(元)
        item = {
            'consumeFee': consumeFee,
            'exposureCnt': exposureCnt,
            'clickCnt': clickCnt,
            'paymentOrder': paymentOrder,
            'paymentAmt': paymentAmt,
            'productRoi': productRoi,
            'clickRate': clickRate,
            'thousandexposureCost': thousandexposureCost,
            'DepaymentOrderQty': DepaymentOrderQty,
            'DepaymentAmt': DepaymentAmt,
            'clickConversionRate': clickConversionRate,
            'orderCost': orderCost,
            'DeCollectOrderNumber': DeCollectOrderNumber,
            'CollectOrderCost': CollectOrderCost
        }
        return item

    def get_ad_overview(self, account, sdate):
        """
        :param account: 用户
        :param sdate: 日期范围
        :return:
        """
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://stark.dewu.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://stark.dewu.com/main/newAdv/advHome',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        sign, timestamp = self.run_node_script(get_file_path('wasm_sign.js'), sdate, self.ad_accessToken).split(" ")
        json_data = {
            'dateType': None,
            'startTimeStr': sdate,
            'endTimeStr': sdate,
            'sceneCodes': [
                0,
                1,
                4,
            ],
            'access_token': self.ad_accessToken,
            'app_key': 'f22f35254aff49c0b032b59b55d4286b',
            'timestamp': int(timestamp),
            'sign': sign,
        }
        response = requests.post(
            'https://stark.dewu.com/api/dewu/cjg/v1/ad/data/overview',
            cookies=self.sensor_cookies,
            headers=headers,
            json=json_data,
            timeout=15
        )
        if response.status_code != 200:
            logger.info(f'得物-营销-推广数据 {sdate} 采集失败')
            return
        ret_data = response.json()['data']
        if not ret_data:
            return
        new_data = self.etl_data(ret_data)
        new_data['account'] = account
        new_data['dt'] = sdate.replace('-', '')
        self.data_list.append(new_data)

    def main(self):
        user_infos = self.tidb.get_user_info('DW')
        for dw_info in user_infos:
            account = dw_info['account']
            self.init_user_cookies(RedisKeys.DW_STARK_LOGIN_KEY.value, account)
            token_result = self.token_replace()  # 替换token
            if not token_result:
                continue
            for sdate in self.generate_date_list(in_day=7):
                self.get_ad_overview(account, sdate)
            self.save_to_tidb(ods_cd_sl_dw_ad_promotion_db_table,
                              ods_cd_sl_dw_ad_promotion_i_d_field_list, self.data_list)
            logger.info(f'得物-营销-推广数据 {account} {len(self.data_list)} 采集完成')
            self.data_list.clear()


if __name__ == "__main__":
    crawler = CrawlerDwPromotionData()
    crawler.main()

