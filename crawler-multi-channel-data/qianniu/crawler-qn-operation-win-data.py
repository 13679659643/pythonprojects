# -*- coding: utf-8 -*-
# @Time    : 2024/12/16 15:36
# @Author  : Night
# @File    : crawler-qn-operation-win-data.py
# @Description:
import time
from datetime import datetime, timedelta
import re
import requests
from base.crawler_base import CrawlerBase
from qianniu.db_model import ods_cd_sl_qn_operation_win_data_i_d_db_table, \
    ods_cd_sl_qn_operation_win_data_i_d_field_list
from settings import RedisKeys
from loguru import logger


class CrawlerQnOperationWinData(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.data_list = []
        self.token = ""


    def etl_data(self, data: dict):
        """
        处理数据，确保所有缺失的 'value' 键都有默认值 0。
        :param data: 包含原始数据的字典
        :return: 处理后的数据项
        """

        def get_value(key, default=0, rounding=None):
            # 尝试从数据中获取子字典，如果不存在则返回包含默认值的字典
            sub_dict = data.get(key, {})
            value = sub_dict.get('value', default)
            # 检查值是否是数字，如果不是则使用默认值
            if not isinstance(value, (int, float)):
                value = default
            # 如果指定了四舍五入的小数位数，则对值进行四舍五入
            if rounding is not None and isinstance(value, (int, float)):
                value = round(value, rounding)
            return value

        item = {
            'adStrategyAmt': get_value('adStrategyAmt', rounding=2),  # 智能场景花费
            'admCostFamtQzt': get_value('admCostFamtQzt',rounding=2),  # 全站推广花费
            'cartByrCnt': get_value('cartByrCnt'),  # 加购人数
            'cartCnt': get_value('cartCnt'),  # 加购件数
            'cartItemCnt': get_value('cartItemCnt'),  # 加购件数
            'cltItmCnt': get_value('cltItmCnt'),  # 商品收藏人数
            'cubeAmt': get_value('cubeAmt',rounding=2),  # 精准人群推广花费
            'descScore': get_value('descScore'),
            'feedCharge': get_value('feedCharge'),
            'oldRepeatByrRate': get_value('oldRepeatByrRate'),  # 老客复购率
            'olderPayAmt': get_value('olderPayAmt'),  # 老买家支付金额
            'p4pExpendAmt': get_value('p4pExpendAmt',rounding=2),  # 关键词推广花费
            'payAmt': get_value('payAmt', rounding=2),  # 支付金额
            'payByrCnt': get_value('payByrCnt'),  # 支付买家数
            'payItmCnt': get_value('payItmCnt'),  # 支付件数
            'payOldByrCnt': get_value('payOldByrCnt'),  # 支付老买家数
            'payOrdByrCnt365': get_value('payOrdByrCnt365'),  # 支付老买家数(365天)
            'payOrdCnt': get_value('payOrdCnt'),  # 支付子订单数
            'payPct': get_value('payPct', rounding=2),  # 客单价
            'payRate': get_value('payRate', rounding=4),  # 支付转化率
            'pv': get_value('pv'),  # 浏览量
            'rfdSucAmt': get_value('rfdSucAmt'),  # 成功退款金额
            'stayTime': get_value('stayTime'),
            'subPayOrdAmt': get_value('subPayOrdAmt',rounding=2),  # 支付金额
            'subPayOrdSubCnt': get_value('subPayOrdSubCnt', rounding=2),  # 支付子订单数
            'tkExpendAmt': get_value('tkExpendAmt',rounding=2),  # 淘宝客佣金
            'uv': get_value('uv'),  # 访客数
            'zzExpendAmt': get_value('zzExpendAmt'),
        }
        return item

    def get_legalityToken(self):
        """
        获取登录 legalityToken  009a6ca8c
        """
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
        }
        date = datetime.now().strftime("%Y-%m-%d")
        dateRange = date + "|" + date
        params = {
            'activeKey': 'operator',
            'dateRange': dateRange,
            'dateType': 'day',
        }
        response = requests.get('https://sycm.taobao.com/portal/home.htm', params=params, cookies=self.cookies,
                                headers=headers)
        match = re.search(r'legalityToken=([^;]+)', response.text)
        if match:
            self.token = match.group(1)

    def getShopMainIndexes(self, account, s_date):
        """
        运营视窗数据
        """
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'bx-v': '2.5.22',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://sycm.taobao.com/portal/home.htm?activeKey=operator&dateRange=2024-12-15%7C2024-12-15%2C2024-12-14%7C2024-12-14&dateType=compareRange',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        # 前一天时间
        one_day_before = datetime.strptime(s_date, '%Y-%m-%d') - timedelta(days=1)
        fm_date = one_day_before.strftime('%Y-%m-%d')
        dateRange = s_date + "|" + s_date + "," + fm_date + "|" + fm_date
        params = {
            'dateType': 'compareRange',
            'dateRange': dateRange,
            'device': '0',
            '_': str(int(time.time() * 1000)),
            'token': self.token,
        }

        response = requests.get(
            'https://sycm.taobao.com/portal/long/period/nodistinct/coreIndex/getShopMainIndexes.json',
            params=params,
            cookies=self.cookies,
            headers=headers,
        )
        if response.status_code != 200:
            return
        ret_data = response.json()['content']['data']
        if not ret_data:
            return
        new_data = self.etl_data(ret_data)
        new_data['account'] = account
        new_data['dt'] = s_date.replace('-', '')
        self.data_list.append(new_data)

    def main(self):
        user_infos = self.tidb.get_user_info('TB')
        for dw_info in user_infos:
            account = dw_info['account']
            self.init_user_cookies(RedisKeys.TB_MYSELLER_LOGIN_KEY.value, account)
            self.get_legalityToken()
            for sdate in self.generate_date_list(in_day=7):
                self.getShopMainIndexes(account, sdate)
            self.save_to_tidb(ods_cd_sl_qn_operation_win_data_i_d_db_table,
                              ods_cd_sl_qn_operation_win_data_i_d_field_list, self.data_list)
            logger.info(f'千牛-运营视窗-数据看板 {account} {len(self.data_list)} 采集完成')
            self.data_list.clear()


if __name__ == "__main__":
    crawler = CrawlerQnOperationWinData()
    crawler.main()
