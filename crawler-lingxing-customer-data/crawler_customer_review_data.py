# -*- coding: utf-8 -*-
# @Time    : 2024/07/25
# @Author  : night
# @Email   :
# @File    :
# @Software: 采集 客服评论review 数据
from crawler_base import BaseCrawler
from datetime import datetime, timedelta
import requests
from settings import URL_REVIEW_API, db_name, table_name, mongo_field_list
from digiCore import Decorate
from loguru import logger


class CrawlerCustomerReview(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.headers = None
        self.start_date = None
        self.end_date = None
        self.table_ob = self.mongo_ob.load_table_ob(db_name, table_name)

    @Decorate.def_retry(msg="客服评论请求 接口失败，正在重试！")
    def get(self, offset=0, _code=1):
        demo_json = {'sort_field': 'review_date', 'sort_type': 'desc', 'search_field': 'amazon_order_id',
                     'search_value': '',
                     'start_date': self.start_date, 'end_date': self.end_date, 'date_field': 'review_time',
                     'offset': offset,
                     'length': 200,
                     'cids': '', 'global_tag_ids': '', 'match_types': '',
                     'req_time_sequence': '/api/customer_service/showReview$$13'}
        rsp = requests.get(url=URL_REVIEW_API, headers=self.headers, params=demo_json).json()
        code = rsp.get("code")
        if int(code) != _code:
            return {}
        return rsp

    def init_task(self, days=30):
        now_date = datetime.now()
        self.end_date = now_date.strftime('%Y-%m-%d')
        self.start_date = (now_date - timedelta(days=days)).strftime('%Y-%m-%d')
        response = self.get()
        total = response.get('total')
        offset_list = [i * 200 for i in range(0, (int(total) - 1) // 200 + 1)]
        logger.info(f'客服评论 生成任务{total} 条')
        return offset_list

    def customer_task(self, task):
        """
        task 任务消费
        """
        response = self.get(offset=task)
        if not response:
            logger.info(f'{task} 此任务请求失败')
            return
        data_list = response.get('list', [])
        if not data_list:
            return
        new_data_List = []
        for data in data_list:
            data['dt'] = data['review_date'].replace('-', '')
            new_data_List.append(data)
        # 数据存入到mongodb
        self.mongo_ob.bulk_save_data(new_data_List, mongo_field_list, self.table_ob)

    def main(self, days=30):
        self.headers = self.get_available_headers()
        task_list = self.init_task(days)
        while len(task_list):
            task = task_list.pop()
            self.customer_task(task)
        logger.info('客服评论数据同步完成')


if __name__ == "__main__":
    cus = CrawlerCustomerReview()
    cus.main()
