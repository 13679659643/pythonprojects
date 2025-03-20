# -*- coding: utf-8 -*-
# @Time    : 2025/03/14 09:14
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import random
import time
from datetime import datetime, timedelta
import requests
from loguru import logger
from base.crawler_base import CrawlerBase, RetryDecorator
from data_pipeline.mongo_tidb_transfer_orderlist import MongoTidbTransferOrderList
from digiCore.db.tidb.core import TiDBDao

from data_pipeline.mongo_tidb_transfer_return_refund import MongoTidbTransferReturnRefund
from db_model import ods_cd_sl_temu_seller_orderlist_i_d_db_table, ods_cd_sl_temu_seller_orderlist_i_d_field_list, \
    ods_cd_sl_temu_seller_return_refund_i_d_db_table, ods_cd_sl_temu_seller_return_refund_i_d_field_list, \
    ods_cd_sl_temu_seller_return_refund_detail_i_d_db_table, ods_cd_sl_temu_seller_return_refund_detail_i_d_field_list
from settings import db_name, mg_orderlist_field_list, orderlist_table_name, domain_url_list, return_refund_table_name, \
    mg_return_refund_list
from login.temu_login import AuthTemuLogin


class CrawlerTemuCentralReturnRefund(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.return_refund_data = []
        self.mallId = ''
        self.mallName = ''
        self.table_ob = self.mongo_ob.load_table_ob(db_name, return_refund_table_name)
        self.seller_temp_cookies = ''
        self.tidb_ob = TiDBDao()
        self.now_date = datetime.now()
        self.startDate = (self.now_date - timedelta(days=61)).strftime('%Y-%m-%d 00:00:00')
        self.endDate = self.now_date.strftime('%Y-%m-%d 23:59:59')
        self.domain_url = ''
        self.detail_payload = []
        self.headers = {}
        self.return_details = []
        self.detail_count = 0

    @RetryDecorator.retry(max_attempts=3)
    def get_productlist(self, pageNo: int = 1):
        """
        temu-跨境卖家中心-订单管理-订单列表-退货退款
        """
        self.headers = {
            # 'authority': 'agentseller-us.temu.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            # 'cookie': 'api_uid=Cp13kmduaTJ0RQBAcuf/Ag==; _bee=x4I7rions1tAxxkV81qRcmfJKKTgPapr; njrpl=x4I7rions1tAxxkV81qRcmfJKKTgPapr; dilx=Z9u45EO7eVShaHa1VWo5U; hfsc=L3yJfYs44Djw057FeA==; _nano_fp=XpmYXpPxn598XqdoXC_Saa9rwEELlHwfb6RMFxhk; timezone=Asia%2FShanghai; webp=1; region=0; mallid=634418216187136; seller_temp=N_eyJ0IjoiWVJhQTR4eldQOEptUC8zck53cGdxR3U3UU5tQmE2V3JPcmxDR0hSMFQxWTVucUNscEtHZXVkVGxlc0ZJU2ZiUThXMW42eDBvQ005TWJsQTFtUC9JOWc9PSIsInYiOjEsInMiOjEwMDAxLCJ1IjoyMTkzNzMxNjMzMzA5NH0=',
            'mallid': self.mallId,
            # 'origin': 'https://agentseller-us.temu.com',
            'pragma': 'no-cache',
            # 'referer': 'https://agentseller-us.temu.com/mmsos/return-refund-list.html?init=true&mallId=634418216187136&uId=21937316333094',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            # 'x-document-referer': 'https://agentseller.temu.com/',
            'x-phan-data': '0aeJxNybENgDAMBEChMA4Ftj_8exbE8hkEUZmkPN1o-2mjvdtthKUB7mF5lEiGSnIi_hOQilJ6j-5TpNkiiVNiLpe68HwnJx1Q',
        }

        json_data = {
            'pageNumber': pageNo,
            'pageSize': 100,
            'startCreatedTime': int(CrawlerBase.timestamp(self.startDate)),
            'endCreatedTime': int(CrawlerBase.timestamp(self.endDate)),
            'groupSearchType': 0,
            'timeSearchType': 5000,
            'reverseSignedTimeSearchType': 7000,
            'selectOnlyRefund': True,
            'selectReturnRefund': True,
        }

        response = requests.post(
            f'{self.domain_url}/garen/mms/afterSales/queryReturnAndRefundPaList',
            cookies=self.seller_temp_cookies,
            headers=self.headers,
            json=json_data,
        )
        if not response.json()['result']:
            logger.info(response.json())
            return None
        if response.status_code == 200:
            return response.json()
        return None

    def fetch_all_pages(self, ):
        """
        获取所有页面的数据
        """
        page_ct = 1
        has_more = True
        while has_more:
            ret_data = self.get_productlist(page_ct)
            if not ret_data['result']['mmsPageVO']['data']:
                break
            total = ret_data['result']['mmsPageVO']['totalCount']
            return_refund_list = ret_data['result']['mmsPageVO']['data']
            for return_refund in return_refund_list:
                return_refund['mallId'] = self.mallId
                return_refund['mallName'] = self.mallName
                return_refund['domain_url'] = self.domain_url
                return_refund['dt'] = CrawlerBase.date_str(
                    CrawlerBase.timestr(return_refund['createdAt']))  # 创建时间yyyyMMdd
                detail_payload_dist = {
                    'dt': return_refund['dt'],
                    'parentAfterSalesSn': return_refund['parentAfterSalesSn'],
                    'parentOrderSn': return_refund['parentOrderSn'],
                }
                self.detail_payload.append(detail_payload_dist)
            page_total_ct = (total - 1) // 100 + 1
            self.return_refund_data.extend(return_refund_list)
            has_more = page_ct < page_total_ct
            page_ct += 1
            time.sleep(random.choice([0.5, 1]))  # 可选：添加延迟避免频繁请求

    def etl_return_details(self, ):
        for payload in self.detail_payload:
            json_data = {
                'parentOrderSn': payload['parentOrderSn'],
                'parentAfterSalesSn': payload['parentAfterSalesSn'],
            }

            response = requests.post(
                f'{self.domain_url}/garen/mms/afterSales/queryReturnDetails',
                cookies=self.seller_temp_cookies,
                headers=self.headers,
                json=json_data,
            )
            if not response.json()['result']:
                logger.info(response.json())
                return
            if response.status_code != 200:
                logger.info(response.json())
                return
            result = response.json()['result']
            afterSalesItemVOList = result['afterSalesItemVOList']
            self.detail_count = self.detail_count + len(afterSalesItemVOList) - 1
            for SalesIetm in afterSalesItemVOList:
                data = {
                    'dt': payload['dt'],  # 售后时间
                    'parentAfterSalesSn': payload['parentAfterSalesSn'],  # 售后单号
                    'parentOrderSn': payload['parentOrderSn'],  # 子订单号
                    'afterSalesSn': SalesIetm.get('afterSalesSn'),  # 售后子单号
                    'goodsThumbUrl': SalesIetm.get('goodsThumbUrl'),  # 鞋子图片
                    'goodsName': SalesIetm.get('goodsName'),  # 标题
                    'goodsSpec': SalesIetm.get('goodsSpec'),  # 属性
                    'productSkuId': SalesIetm.get('productSkuId'),  # 货号颜色尺码,SKU是对可以独立管理、独立核算、独立销售的最小单位进行编码的结果
                    'applyReturnGoodsNumber': SalesIetm.get('applyReturnGoodsNumber'),  # 应退数量
                    'returnGoodsNumber': SalesIetm.get('returnGoodsNumber'),  # 同意退款数量
                    'rejectGoodsNumber': SalesIetm.get('rejectGoodsNumber'),  # 拒绝退款数量
                    'afterSalesReasonDesc': SalesIetm.get('afterSalesReasonDesc'),  # 退货原因
                    'refundStatusDesc': SalesIetm.get('refundStatusDesc'),  # 退款状态
                    'rejectReasonDesc': SalesIetm.get('rejectReasonDesc'),  # 拒绝原因
                    'applyRefundAmountStr': SalesIetm.get('applyRefundAmountStr'),  # 买家申请退款的金额
                    'initRefundAmountStr': SalesIetm.get('initRefundAmountStr'),  # 起始退款金额
                    'refundAmount': SalesIetm.get('refundAmount'),  # 实际退款金额
                    'name': result['afterSalesFlowNodeVOList'][0]['name'],  # 售后记录name
                    'desc': result['afterSalesFlowNodeVOList'][0]['desc'],  # 售后记录name
                    'timeStr': result['afterSalesFlowNodeVOList'][0]['timeStr'],  # 售后记录timeStr
                    'mallName': self.mallName,  # 店铺名称
                    'mallId': self.mallId,  # 店铺id
                    'domain_url': self.domain_url,  # 域名
                }
                self.return_details.append(data)


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
        time.sleep(random.choice([0.5, 1]))
        UserInfo = self.userInfo()
        mall_info_list = CrawlerBase().mallId(UserInfo)
        for userinfo in mall_info_list:
            self.mallId = str(userinfo['mallId'])
            self.mallName = userinfo['mallName']
            for domain_url in domain_url_list:
                self.return_refund_data.clear()  # 清空列表 list 放在此处避免重试时累计值
                self.detail_payload.clear()

                self.domain_url = domain_url
                verify_code = self.get_code(self.cookies, self.domain_url)
                self.seller_temp_cookies = self.loginByCode(verify_code, self.domain_url)
                self.fetch_all_pages()
                if not self.return_refund_data:
                    continue
                self.mongo_ob.bulk_save_data(self.return_refund_data, mg_return_refund_list, self.table_ob)
                logger.info(
                    f'temu-跨境卖家中心-订单管理-订单列表-退货退款 {account} {self.mallName} {len(self.return_refund_data)} 存入mongo完成 {self.domain_url}')
                self.etl_return_details()

    def main(self):
        deleted_mongodb_count = self.delete_mongodb_one_month(return_refund_table_name)
        logger.info(f'删除 mongodb 退货退款 近61天： {deleted_mongodb_count} 条数据完成')
        user_infos = self.tidb.get_user_info('TEMU')
        for temu_info in user_infos:
            account = temu_info['account']
            # if account == '13074832078':
            password = temu_info['password']
            self.run(account, password)
        etl_return_refund_list = MongoTidbTransferReturnRefund().etl_return_refund_list()
        self.save_to_tidb(ods_cd_sl_temu_seller_return_refund_i_d_db_table,
                          ods_cd_sl_temu_seller_return_refund_i_d_field_list, etl_return_refund_list)
        logger.info(f'temu-跨境卖家中心-订单管理-订单列表-退货退款 {len(etl_return_refund_list)} 条数据采集完成')

        self.save_to_tidb(ods_cd_sl_temu_seller_return_refund_detail_i_d_db_table,
                          ods_cd_sl_temu_seller_return_refund_detail_i_d_field_list, self.return_details)
        logger.info(f'详情:由于一个订单可能会出现多双退货，所以在此统计会增加的行数: {self.detail_count} 行！')
        logger.info(f'temu-跨境卖家中心-订单管理-订单列表-退货退款详情信息 {len(self.return_details)} 条数据采集完成')



if __name__ == "__main__":
    crawler = CrawlerTemuCentralReturnRefund()
    crawler.main()
