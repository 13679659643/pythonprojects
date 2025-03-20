# -*- coding: utf-8 -*-
# @Time    : 2023/8/11 17:41
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    : 
# @Software: 同步领星财务-亚马逊结算中心-结算汇总
import json

import requests
from digiCore import Decorate
from digiCore.utils import DateTool
from digiCore.model import WebEnum
from loguru import logger

from common_resources import CrawlerBase
from db_model import ods_fc_gad_lx_settlement_summary_i_d_field_list, \
    ods_gsm_lx_amz_settlement_summary
from settings import fc_settlement_summary_api_url


class FcSettlementSummary(CrawlerBase):

    def get_days(self):
        sql = """
                select run_cycle from dim_prod.dim_dsd_me_server_scheduler_i_manual where service_name = 'query_clearing_center_summary' LIMIT 1;
                """
        days = self.tidb_ob.query_one(sql).get('run_cycle', 14)
        return days

    @Decorate.def_retry(msg="领星财务-亚马逊结算中心-结算汇总 请求失败！")
    def get_response(self, start_date, end_date, offset=0, length=100, _code=1):
        """
        请求数据
        :return:
        """
        json_data = {
            'dateType': '0',
            'processingStatus': '',
            'fundTransferStatus': '',
            'searchField': 'id',
            'searchValue': [],
            'currencyCode': '',
            'receivedState': '',
            'sids': '',
            'countryCodes': '',
            'startDate': start_date,
            'endDate': end_date,
            'offset': offset,
            'length': length,
            'accountType': [],
            'reconciliationResult': [],
            'receivableSymbol': '',
            'receivableValue': '',
            'transferSymbol': '',
            'transferValue': '',
            'sortField': 'financialEventGroupStartLocale',
            'sortType': 'desc',
            'req_time_sequence': '/bd/sp/api/settlement/summary/list$$1',
        }
        _headers = self.init_headers()
        response = requests.post(url=fc_settlement_summary_api_url, json=json_data, headers=_headers).json()
        if response.get('code') == _code:
            return response
        else:
            return WebEnum.STATUS_ERROR

    def get_task_list(self, start_date, end_date, pages):
        task_list = []
        for i in range(0, pages):
            task_json = {}
            task_json["start_date"] = start_date
            task_json["end_date"] = end_date
            task_json["offset"] = i * 100
            task_list.append(task_json)
        return task_list

    def init_task(self):
        """
        初始化任务
        :return:
        """
        days = self.get_days()
        start_date, end_date = DateTool.get_task_date(days)
        response = self.get_response(start_date, end_date)
        pages = response.get('data')['pages']
        task_list = self.get_task_list(start_date, end_date, pages)
        logger.info(f"亚马逊结算中心-结算汇总 生成任务队列 {len(task_list)} 条！")
        return task_list

    def init_consumer(self, task_list):
        """
        消费任务队列
        :param task_list:
        :return:
        """
        for task in task_list:
            response = self.get_response(task.get('start_date'),
                                         task.get('end_date'),
                                         task.get('offset'))
            if response == WebEnum.STATUS_ERROR:
                logger.info('{task}  此任务请求失败')
                break
            data = response.get("data", [])
            if not data:
                continue
            records = data.get("records")
            data_list = self.etl_data_list(records)
            self.tidb_save(data_list)
        logger.info("crawler:领星财务-亚马逊结算中心-结算汇总 任务消耗完成，程序退出！")

    def etl_data_list(self, records):
        data_list = []
        for data in records:
            data["dt"] = data.get("financialEventGroupStartLocale").split("T")[0].replace('-', '')
            data["sale"] = json.dumps(data["sale"])
            data["refund"] = json.dumps(data["refund"])
            data["pay"] = json.dumps(data["pay"])
            data["transfer"] = json.dumps(data["transfer"])
            if not data['id']:
                continue
            data_list.append(data)
        return data_list

    def tidb_save(self, data_list):
        self.tidb_ob.insert_data(ods_gsm_lx_amz_settlement_summary, ods_fc_gad_lx_settlement_summary_i_d_field_list,
                                 data_list)

    def main(self):

        task_list = self.init_task()
        self.init_consumer(task_list)
        return WebEnum.STATUS_SUCCESS


if __name__ == "__main__":
    FcSettlementSummary().main()
