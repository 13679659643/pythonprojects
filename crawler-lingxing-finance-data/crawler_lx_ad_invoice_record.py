# _*_ coding: utf-8 _*_
# @Time : 2024/3/15
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-finance-data
# @Desc : 领星-财务-广告发票记录
import time

from digiCore.utils import DateTool
from loguru import logger

from common_resources import CrawlerBase
from db_model import ods_gsm_lx_ad_invoice_record, ods_gsm_lx_ad_invoice_record_i_d_field_list


class CrawlerLingxingInvoiceRecord(CrawlerBase):

    url = 'https://gw.lingxingerp.com/bd/profit/report/report/ads/invoice/list'

    def init_task(self):
        """
        创建近7天的数据请求任务
        """
        days = self.extra_params.get('days',7)
        start_date, end_date = DateTool.get_task_date(days)
        json_data = {
            'offset': 0,
            'length': 100,
            'invoiceStartTime': f'{start_date}',
            'invoiceEndTime': f'{end_date}',
            'searchType': 'ads_campaign'
        }
        return json_data

    def consume_task(self, task):

        record_list = []
        while True:
            response = self.post(self.url, task)
            if response.get('code') != 1:
                time.sleep(5)
                continue
            data = response.get('data')
            records = data.get('records')
            if not records:
                break

            task['offset'] += task['length']
            logger.info(f'继续请求下一页offset：{task.get("offset")} ！')
            format_data_list = self.format_data(records, task)
            record_list += format_data_list
        return record_list

    def format_data(self, records, task):

        data_list = []
        for record in records:
            record.pop('campaignInfo')
            record['dt'] = record['invoiceDate'].replace('-', '')
            data_list.append(record)
        return data_list

    def main(self):
        """
        1、补全历史数据
        2、同步更新进一周数据
        3、创建任务，生成任务队列
        4、消耗任务，获取页面数据
        5、清洗数据，保存到数据库
        """
        # 历史数据 20240201--20240315
        task = self.init_task()
        record_list = self.consume_task(task)
        if not record_list:
            return

        self.tidb_ob.insert_data(ods_gsm_lx_ad_invoice_record, ods_gsm_lx_ad_invoice_record_i_d_field_list, record_list)
        logger.info(f'广告发票记录列表页-近7天广告发票记录更新完成：{len(record_list)} !')


if __name__ == '__main__':
    c = CrawlerLingxingInvoiceRecord()
    c.main()
