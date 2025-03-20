# -*- coding: utf-8 -*-
# @Time    : 2023/5/23 15:52
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    :
# @Software:
import time

from digiCore import Decorate
from digiCore.model import WebEnum
from digiCore.utils import DateTool
from loguru import logger

from common_resources import CrawlerBase
from db_model import ods_fc_gad_lx_profit_report_order_i_w_field_list, ods_fc_gad_lx_profit_report_order_i_w, \
    profit_report_order_db_table
from settings import report_order_url


class CrawlerProfitReportOrderData(CrawlerBase):


    @Decorate.def_retry(msg="请求利润报表（订单）接口失败，正在重试！")
    def get_response(self, start_date, end_date, offset=0, length=1000, _code=1):
        """
        用于请求利润报表（订单）货件的数量
        :return:
        """
        json_data = {
            "offset": offset,
            "length": length,  # 偏移量
            "startDate": start_date,  # 开始时间
            "endDate": end_date,  # 结束时间
            "searchField": "order_id",
            "sortField": "postedDatetimeLocale",
            "sortType": "desc",
            "searchDateField": "posted_date_locale"
        }
        response = self.post(url=report_order_url, data=json_data)
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
        logger.info(f"crawler-利润报表（订单）生成任务队列 {len(task_list)} 条")
        self.delete_tidb_data(days)
        return task_list

    def get_days(self):
        sql = """
                select run_cycle from dim_prod.dim_dsd_me_server_scheduler_i_manual where service_name = 'crawler_lingxing_profit_report_order' LIMIT 1;
                """
        days = self.tidb_ob.query_one(sql).get('run_cycle', 14)
        return days

    def delete_tidb_data(self, days):
        """
        获取程序时，需先删除所获取时间的数据
        :return:
        """
        sql = f"""
            DELETE FROM {profit_report_order_db_table} WHERE `dt` >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL {days} DAY), '%Y%m%d')
        """
        self.tidb_ob.commit_sql(sql)
        logger.info(f"删除表{profit_report_order_db_table} {days} 天内的数据")
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
        logger.info("crawler:领星-利润报表（订单） 任务消耗完成，程序退出！")

    def etl_data_list(self, records):
        data_list = []
        for data in records:
            data["dt"] = data.get("postedDatetimeLocale").split(" ")[0].replace("-", "")
            if not data['id']:
                continue
            data_list.append(data)
        return data_list

    def tidb_save(self, data_list): 
        sql = ods_fc_gad_lx_profit_report_order_i_w.replace('\n', ' ')
        self.tidb_ob.commit_sql(sql)
        self.tidb_ob.insert_data(profit_report_order_db_table, ods_fc_gad_lx_profit_report_order_i_w_field_list,
                                 data_list)

    def main(self):

        task_list = self.init_task()

        self.customer_task(task_list)
        return WebEnum.STATUS_SUCCESS


if __name__ == '__main__':
    sapr = CrawlerProfitReportOrderData()
    sapr.main()
