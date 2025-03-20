# _*_ coding: utf-8 _*_
# @Time : 2024-12-26
# @Author : 李仕春
# @Email ： scli@doocn.com
# @File : crawler-lingxing-finance-data
# @Desc : 采集-利润报表-订单transaction视图
import json
import time

from digiCore import Decorate
from digiCore.model import WebEnum
from digiCore.utils import DateTool
from loguru import logger

from common_resources import CrawlerBase
from db_model import ods_gsm_lx_profit_report_order_transaction_table, ods_gsm_lx_profit_report_order_transaction_i_d, \
    ods_gsm_lx_profit_report_order_transaction_dict
from settings import report_order_transaction_url


class CrawlerProfitReportOrderTransaction(CrawlerBase):


    @Decorate.def_retry(msg="请求利润报表（订单transaction视图） 接口失败，正在重试！")
    def get_response(self, start_date, end_date, offset=0, length=1000, _code=1):
        """
        用于请求利润报表（订单）货件的数量
        :return:
        """
        json_data = {
            'offset': offset,
            'length': length,
            'mids': [],
            'sids': [],
            'startDate': start_date,
            'endDate': end_date,
            'currencyCode': '',
            'searchField': 'order_id',
            'searchValue': [],
            'sortField': 'postedDatetimeLocale',
            'sortType': 'desc',
            'settlementStatus': [],
            'fundTransferStatus': [],
            'searchDateField': 'posted_date_locale',
            'accountType': [],
            'eventSource': [],
            'fulfillment': [],
            'principalUids': [],
            'productDeveloperUids': [],
            'orderStatus': 'All',
            'req_time_sequence': '/bd/profit/report/report/transaction/list$$12',
        }
        response = self.post(url=report_order_transaction_url, data=json_data)
        code = response.get("code")
        if int(code) != _code:
            return {}
        return response

    def init_task(self):
        """
        初始化任务
        通过获取total来生成任务
        :return:
        """
        days = self.get_days()
        start_date, end_date = self.get_date(days)
        response = self.get_response(start_date, end_date)
        pages = response["data"]["pages"]
        task_list = self.get_task_list(start_date, end_date, pages)
        logger.info(f"crawler-利润报表（订单transaction视图） {start_date} : {end_date} 生成任务队列 {len(task_list)} 条")
        self.delete_tidb_data(days)
        return task_list

    def get_days(self):
        sql = """
                select run_cycle from dim_prod.dim_dsd_me_server_scheduler_i_manual where service_name = 'crawler_lx_profit_report_order_transaction' LIMIT 1;
                """
        days = self.tidb_ob.query_one(sql).get('run_cycle', 14)
        return days

    def delete_tidb_data(self, days):
        """
        获取程序时，需先删除所获取时间的数据
        :return:
        """
        sql = f"""
            DELETE FROM {ods_gsm_lx_profit_report_order_transaction_table} WHERE `dt` >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL {days} DAY), '%Y%m%d')
        """
        self.tidb_ob.commit_sql(sql)
        logger.info(f"删除表{ods_gsm_lx_profit_report_order_transaction_table} {days} 天内的数据")
        time.sleep(2)
        return

    def get_date(self, days):
        start_date, end_date = DateTool.get_task_date(days)
        if start_date < "2023-05-01":
            start_date = "2023-05-01"
        return start_date, end_date

    def get_task_list(self, start_date, end_date, pages):
        task_list = []
        for i in range(0, pages):
            task_json = {}
            task_json["start_date"] = start_date
            task_json["end_date"] = end_date
            task_json["offset"] = i * 1000
            task_list.append(task_json)
        return task_list

    def customer_task(self, task_list):
        """
        消费任务
        :return:
        """
        for task in task_list:
            response = self.get_response(task.get('start_date'),
                                         task.get('end_date'),
                                         task.get('offset'))
            if not response:
                logger.info(f'{task}  此任务请求失败')
                break
            data = response.get("data", [])
            if not data:
                continue
            records = data.get("records")
            data_list = self.etl_data_list(records)
            self.tidb_save(data_list)
        logger.info("crawler:领星-利润报表（订单transaction视图） 任务消耗完成，程序退出！")

    def etl_data_list(self, records):
        data_list = []
        for data in records:
            data["dt"] = data.get("postedDatetimeLocale").split(" ")[0].replace("-", "")
            data["purchaseCostsDetail"] = data.get("purchaseCostsDetail", []) or '[]'
            data["purchaseCostsDetailWeb"] = json.dumps(data.get("purchaseCostsDetailWeb", []) or '[]')
            data["logisticsCostsDetail"] = data.get("logisticsCostsDetail", []) or '[]'
            data["logisticsCostsDetailWeb"] = json.dumps(data.get("logisticsCostsDetailWeb", []) or '[]')
            data["otherCostsDetail"] = data.get("otherCostsDetail", []) or '[]'
            data["otherCostsDetailWeb"] = json.dumps(data.get("otherCostsDetailWeb", []) or '[]')

            data_list.append(data)
        new_data_list = self.original_to_format_key(data_list, ods_gsm_lx_profit_report_order_transaction_dict)
        return new_data_list

    def tidb_save(self, data_list):
        self.tidb_ob.commit_sql(ods_gsm_lx_profit_report_order_transaction_i_d)
        insert_status = self.tidb_ob.insert_data(ods_gsm_lx_profit_report_order_transaction_table,
                                                 ods_gsm_lx_profit_report_order_transaction_dict.values(),
                                                data_list)
        if insert_status != 4001:
            logger.info(f'领星-利润报表（订单transaction视图） 数据保存成功 {len(data_list)} 条！')

    def main(self):
        task_list = self.init_task()
        self.customer_task(task_list)
        return WebEnum.STATUS_SUCCESS

if __name__ == '__main__':
    cprot = CrawlerProfitReportOrderTransaction()
    cprot.main()