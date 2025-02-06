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
from db_model import ods_cd_inv_wfs_stock_i_d_field_list,crawler_lx_platform_wfs_stock_db_table
from settings import wfs_stock_url, mongo_db_field, mongo_db, mongo_db_table


class CrawlerPlatformWfsStock(Base):

    def __init__(self):
        super().__init__()
    def init_task(self):
        """
        初始化任务
        通过获取total来生成任务
        :return:
        """
        task = {
            "current": 0,
            "size": 200
        }
        response = self.post(url=wfs_stock_url, data=task)
        pages = response["data"]["page"]['total']
        task_list = self.get_task_list(pages)
        logger.info(f"crawler-wfs库存 生成任务队列 {len(task_list)} 条")
        return task_list

    def get_task_list(self, pages):
        task_list = []
        for i in range(0, (int(pages) + 200 - 1) // 200):
            task_json = {}
            task_json["current"] = i + 1
            task_json["size"] = 200
            task_list.append(task_json)
        return task_list

    def customer_task(self, task_list):
        """
        消费任务
        :return:
        """
        all_data_list = []
        for task in task_list:
            response = self.post(url=wfs_stock_url, data=task)
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

    def tidb_save(self, all_data_list):
        """
        :param data_list:
        :param db: 表对象
        数据同步到 MongoDB 和 Tidb
        :return:
        """
        db = self.mongo_ob.load_table_ob(mongo_db, mongo_db_table)
        self.mongo_ob.bulk_save_data(all_data_list, mongo_db_field, db)
        self.tidb_ob.insert_data(crawler_lx_platform_wfs_stock_db_table, ods_cd_inv_wfs_stock_i_d_field_list,
                                 all_data_list)

    def main(self):

        task_list = self.init_task()

        all_data_list = self.customer_task(task_list)

        self.tidb_save(all_data_list)
        logger.info("crawler:多平台-wfs库存 任务消耗完成，程序退出！")
        return WebEnum.STATUS_SUCCESS


if __name__ == '__main__':
    sapr = CrawlerPlatformWfsStock()
    sapr.main()
