# -*- coding: utf-8 -*-
# @Time    : 2023/11/15 1
# @Author  : night
# @Email   :
# @File    :
# @Software:
import datetime
from digiCore.model import WebEnum
from loguru import logger

from common_resource import Base
from db_model import ods_cd_inv_fbc_stock_i_d_field_list, crawler_lx_platform_fbc_stock_db_table
from settings import fbc_stock_url


class CrawlerPlatformFbcStock(Base):

    def __init__(self):
        super().__init__()

    def init_task(self):
        """
        初始化任务
        通过获取total来生成任务
        :return:
        """
        task = {"hideZeroStorage": 0, "storeIdList": [], "warehouseList": [], "goodStatusList": [],
                "selectTypeEnum": "COUNT_TYPE", "custom": {"type": 1, "likeContent": "", "inContentList": []},
                "length": 200, "offset": 0, "orderColumnType": "", "orderWay": "",
                "req_time_sequence": "/mp-platform-warehouse-api/api/fbc/stockSearch$$1"}
        response = self.post(url=fbc_stock_url, data=task)
        pages = response["data"]["page"]['total']
        task_list = self.get_task_list(pages)
        logger.info(f"crawler-fbc库存 生成任务队列 {len(task_list)} 条")
        return task_list

    def get_task_list(self, pages):
        task_list = []
        for i in range(0, (int(pages) + 200 - 1) // 200):
            task_json = {}
            task_json["offset"] = i  * 200
            task_json["length"] = 200
            task_list.append(task_json)
        return task_list

    def customer_task(self, task_list):
        """
        消费任务
        :return:
        """
        all_data_list = []
        for task in task_list:
            json_data = {"hideZeroStorage": 0, "storeIdList": [], "warehouseList": [], "goodStatusList": [],
                         "selectTypeEnum": "COUNT_TYPE", "custom": {"type": 1, "likeContent": "", "inContentList": []},
                         "length": task['length'], "offset": task['offset'], "orderColumnType": "", "orderWay": "",
                         "req_time_sequence": "/mp-platform-warehouse-api/api/fbc/stockSearch$$1"}
            response = self.post(url=fbc_stock_url, data=json_data)
            if not response:
                logger.info(f'{task}  此任务请求失败')
                break
            data = response.get("data", {}).get("page", {})
            if not data:
                continue
            records = data.get("records")
            data_list = self.etl_data_list(records)
            all_data_list += data_list
        return all_data_list

    def etl_data_list(self, records):
        data_list = []
        now = datetime.datetime.now().strftime("%Y%m%d")
        for data in records:
            data["dt"] = now
            data['sid'] = data['storeId']
            data.pop('storeId')
            data_list.append(data)
        return data_list

    def main(self):
        task_list = self.init_task()
        all_data_list = self.customer_task(task_list)
        self.tidb_ob.insert_data(crawler_lx_platform_fbc_stock_db_table, ods_cd_inv_fbc_stock_i_d_field_list,
                                 all_data_list)
        logger.info("crawler:多平台-fbc库存 任务消耗完成，程序退出！")
        return WebEnum.STATUS_SUCCESS


if __name__ == '__main__':
    sapr = CrawlerPlatformFbcStock()
    sapr.main()
