# -*- coding: utf-8 -*-
# @Time    : 2025/1/21 14:49
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
from datetime import datetime, timedelta
import random
import time
import requests
from loguru import logger
from base.crawler_base import RetryDecorator
from db_model import ods_cd_sl_temu_seller_illegalidetail_i_d_field_list, \
    ods_cd_sl_temu_seller_illegalidetail_i_d_db_table
from digiCore.db.tidb.core import TiDBDao
from settings import illegalidata


class CrawlerTemuCentralIllegaliDetail:
    """
    最近14天的违规信息详情
    """

    def __init__(self, seller_temp_cookies, mallId, mallName, domain_url):
        super().__init__()
        self.detail_list = []
        self.seller_temp_cookies = seller_temp_cookies
        self.violationappealsn = ''
        self.violationtype = ''
        self.mallId = mallId
        self.mallName = mallName
        # 20250114
        self.start_dt = (datetime.now() - timedelta(days=14)).strftime('%Y%m%d')
        self.tidb_ob = TiDBDao()
        self.domain_url = domain_url

    @RetryDecorator.retry(max_attempts=3)
    def get_listillegalidetail(self, ):
        """
        temu-跨境卖家中心-店铺管理-违规信息详情
        """
        headers = {
            'authority': 'agentseller.temu.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'mallid': self.mallId,
            # 'origin': 'https://agentseller.temu.com',
            'pragma': 'no-cache',
            # 'referer': 'https://agentseller.temu.com/mmsos/mall-appeal.html?targetType=1',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            # 'x-document-referer': 'https://agentseller.temu.com/main/authentication?redirectUrl=https%3A%2F%2Fagentseller.temu.com%2Fmmsos%2Fmall-appeal.html%3FtargetType%3D1',
        }

        json_data = {
            'violationAppealSn': self.violationappealsn,
            'violationType': self.violationtype,
        }

        response = requests.post(
            f'{self.domain_url}/reaper/violation/appeal/querySubTargetAppeals',
            cookies=self.seller_temp_cookies,
            headers=headers,
            json=json_data,
        )
        if response.json()['errorMsg'] == '不存在的违规信息':
            logger.info(response.json())
            return {}
        if response.json()['result'] is None:
            logger.info(response.json())
            return None
        if response.status_code == 200:
            return response.json()
        return {}

    def get_violationappealsn_info(self, ):
        """
        获取数据库违规编码
        :return: violationAppealSn 违规编码
        """
        sql = f"""
                SELECT violationAppealSn,violationType FROM ods_prod.ods_cd_sl_temu_seller_illegalidata_i_d \
                WHERE mallName = '{self.mallName}' AND dt >= '{self.start_dt}' AND domain_url = '{self.domain_url}'
                """

        result_list = self.tidb_ob.query_list(sql)
        return result_list

    @staticmethod
    def get_violationtype(violationType):
        """
        通过数据库获取的违规类型去获取对应的编号
        Args:
            violationType:
        Returns:key
        """
        s = violationType
        for category, mapping in illegalidata.items():
            for key, value in mapping.items():
                if value == s:
                    return key
        return None

    def elt_violation_detail(self, detail_info: dict):
        subTargetList = detail_info.get('result').get('subTargetList')
        for sub in subTargetList:
            item = sub.get('targetAttribute')
            new_item = {
                'violationAppealSn': self.violationappealsn,
                'poNumber': item.get('poNumber'),
                'amount': item.get('amount'),
                'currency': item.get('currency'),
                'promiseTime': item.get('promiseTime'),
                'violationType': self.violationtype,
                'mallId': self.mallId,
                'mallName': self.mallName
            }
            self.detail_list.append(new_item)


    def main(self):

        self.detail_list.clear()  # 清空列表 list
        violationAppealSn_infos = self.get_violationappealsn_info()
        for vas_info in violationAppealSn_infos:

            self.violationappealsn = vas_info['violationAppealSn']
            self.violationtype = self.get_violationtype(vas_info['violationType'])
            detail_info = self.get_listillegalidetail()
            time.sleep(random.choice([0.5, 1]))  # 可选：添加延迟避免频繁请求
            if not detail_info:
                continue
            self.elt_violation_detail(detail_info)

        self.tidb_ob.insert_data(ods_cd_sl_temu_seller_illegalidetail_i_d_db_table,
                                 ods_cd_sl_temu_seller_illegalidetail_i_d_field_list, self.detail_list)
        logger.info(
            f'temu-跨境卖家中心-店铺管理-违规信息详情  {self.mallName} {len(self.detail_list)} 采集完成 {self.domain_url}')


if __name__ == "__main__":
    crawler = CrawlerTemuCentralIllegaliDetail('', '', '', '')
    crawler.main()
