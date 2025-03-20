# _*_ coding: utf-8 _*_
# @Time : 2024/3/15
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-finance-data
# @Desc : 领星-财务-广告发票记录
from loguru import logger
import concurrent.futures
from common_resources import CrawlerBase
from db_model import ods_gsm_lx_ad_invoice_record, ods_gsm_lx_ad_invoice_record_detail, \
    ods_gsm_lx_ad_invoice_record_detail_i_d_field_list


class CrawlerLingxingFinanceData(CrawlerBase):
    url = 'https://gw.lingxingerp.com/bd/profit/report/report/ads/invoice/campaign/list'
    task_list = []
    data_list = []

    def query_ad_record(self):
        """
        查询数据库广告发票记录列表页数据
        """
        sql = f'select dt,invoiceId,sid,invoiceDate from {ods_gsm_lx_ad_invoice_record} where dt >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 WEEK ), "%Y%m%d")'
        ad_invoice_record_list = self.tidb_ob.query_list(sql)
        return ad_invoice_record_list

    def init_task(self, ad_invoice_record_list):
        """
        初始化任务队列
        """
        task_list = []
        for ad_invoice_record in ad_invoice_record_list:
            json_data = {
                'offset': 0,
                'length': 1000,
                'invoiceStartTime': ad_invoice_record['invoiceDate'],
                'invoiceEndTime': ad_invoice_record['invoiceDate'],
                'invoiceId': ad_invoice_record['invoiceId'],
                'sid': ad_invoice_record['sid'],
                'searchType': 'ads_campaign'
            }
            task_list.append(json_data)
        return task_list

    def consume_task(self, task_list):
        """
        获取广告发票详情页数据
        """
        logger.info(f"广告发票记录列表页-详情页数据：采集开始!")
        while True:
            if not self.task_list:
                break
            task = self.task_list.pop()
            response = self.post(self.url, data=task)
            if not response:
                continue
            data = response.get('data')
            records = data.get('records')
            format_data_list = self.format_data(records, task)
            self.data_list += format_data_list

    def format_data(self, records, task):
        """
        格式化数据
        """
        data_list = []
        for record in records:
            record['dt'] = task['invoiceStartTime'].replace('-', '')
            record['invoiceId'] = task['invoiceId']
            record['sid'] = task['sid']
            data_list.append(record)
        return data_list

    def main(self):
        """
        1、查询数据库列表页数据
        2、初始化任务队列
        3、消费任务
        4、格式化数据，保存数据
        """
        ad_invoice_record_list = self.query_ad_record()
        self.task_list = self.init_task(ad_invoice_record_list)

        with concurrent.futures.ThreadPoolExecutor(max_workers=11) as executor:
            futures = [executor.submit(self.consume_task, []) for _ in range(10)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f'任务执行中发生了异常: {e}')

        self.tidb_ob.insert_data(ods_gsm_lx_ad_invoice_record_detail,
                                 ods_gsm_lx_ad_invoice_record_detail_i_d_field_list, self.data_list)
        logger.info(f'广告发票记录详情页-近7天广告发票记录更新完成：{len(self.data_list)} !')


if __name__ == '__main__':
    c = CrawlerLingxingFinanceData()
    c.main()
