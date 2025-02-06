# -*- coding: utf-8 -*-
# @Time    : 2024/8/9 15:34
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:

import requests
import queue
import time

from crawler_base import BaseCrawler
from db_model import truncate_ods_scg_wld_logistics_trace_table_i_d, truncate_ods_scg_wld_logistics_trace_view_i_d
from method import TimestampFormatter, RegularExpressionHtml, \
    DatabaseConnector, list_to_sql_values, create_insert_sql, \
    RetryDecorator, init_redis, BaseCrawlerView
from datetime import datetime, timedelta
from loguru import logger
from jsonpath import jsonpath


class LogisticsDataFetcher_nextsls(BaseCrawler):
    """可以继承其他class，使用self调用."""

    def __init__(self):
        """定义 LogisticsDataFetcher 类"""
        super().__init__()
        # 创建了主页面一个队列，这个队列用于在生产者（数据抓取线程）和消费者（数据处理线程）之间传递数据。队列是线程安全的，可以在多线程环境下进行操作。
        self.data_queue = queue.Queue()
        # 创建采集view详情页面的url数据队列。后续采用从数据库获取状态为all的id
        self.view_id_data_queue = queue.Queue()
        # 创建处理view详情页面的数据队列。
        self.view_data_queue = queue.Queue()
        # 数据插入mysql消费者队列
        self.insert_data_queue = queue.Queue()
        # 定义批量插入(队列)的大小
        self.batch_size = 3
        # 定义插入间隔时间（秒）
        self.insert_interval = 5
        # 初始化会话对象
        self.session = requests.session()
        # 在这里，self.session.headers 是一个字典，.update({...}) 方法用于向这个字典中添加或更新键值对
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        })
        self.redis_client = init_redis().__redis__()
        # 存储详情页面信息
        self.detail_page_data = []
        # 2024-10-16 16:10:55.812744
        self.now_date = datetime.now()
        # '20241016 23:59:59'
        self.end_date = self.now_date.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
        # '20240618 00:00:00'
        self.start_date = (self.now_date - timedelta(days=180)).replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
        T = TimestampFormatter()
        self.end_unix = T.format_tostring(self.end_date)
        self.start_unix = T.format_tostring(self.start_date)

    @RetryDecorator.retry_decorator(msg="采集数据出错", error_type=713, max_retry_count=3, time_interval=1)
    def fetch_page_data(self, shipped_status: str, page=1):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""
        fetch_json_data = {
            'timeLimit': 0,
            'page': page,
            'activeTab': shipped_status,
            'isActiveTab': 'all',
            'scenes': 1,
            'created_daterange': [self.start_unix, self.end_unix]
        }
        response = self.session.post(self.data_url, json=fetch_json_data)
        if response.status_code != 200:
            return {}
        return response.json()

    def get_total_pages(self, data_dict: dict):
        """
        根据响应数据获取分页信息
        :param data_dict: 初始响应数据
        :return: 总页数
        """
        if not data_dict:
            return 0
        # 获取总行数（total_rows）和每页的大小（page_size）
        total_rows = data_dict['data']['components']['gridView']['table']['pagination']['total']
        page_size = data_dict['data']['components']['gridView']['table']['pagination']['pageSize']
        # 将总行数加上每页大小减一,然后整除每页大小来完成的.这样做是为了确保如果总行数不能被每页大小整除时,总页数会向上取整.
        total_pages = (total_rows + page_size - 1) // page_size

        return total_pages

    def process_data(self, page_data: dict, shipped_status: str):
        """处理每页的数据"""
        page_dataSource = page_data['data']['components']['gridView']['table']['dataSource']
        reh = RegularExpressionHtml()
        tf = TimestampFormatter()
        try:
            for item in page_dataSource:
                date_str = TimestampFormatter.format_timestamp(item['created'])
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                formatted_date = date.strftime("%Y%m%d")
                courier_number = reh.extract_html_info(item['outer_carrier'])[1]
                # remark = data.get('remark', '')
                # match = re.search('OWS\d+', remark)
                # if match:
                #     print(match.group())
                item["dt"] = formatted_date
                item['logistics_provider'] = self.logistics_provider
                item['shipment_id'] = reh.extract_logistics_codes(item['shipment_id'])
                item['to_address_country'] = reh.extract_replace_str(item['to_address_country'])
                item['parcel_count'] = reh.extract_html_font(item['parcel_count'])
                item['actual_weight'] = reh.extract_html_font(item['actual_weight'])
                # 　get() 方法接受两个参数：键和默认值。如果字典中存在这个键，get() 方法会返回这个键对应的值；如果字典中不存在这个键，get() 方法会返回默认值。
                item['actual_volume'] = reh.extract_html_font(item.get('actual_volume', 'None'))
                item['actual_volume_weight'] = reh.extract_html_font(item['actual_volume_weight'])
                item['exportwith'] = reh.extract_html_sapn(item['exportwith'])
                item['outer_carrier'] = reh.extract_html_info(item['outer_carrier'])[0]
                item['courier_number'] = courier_number
                item['printed'] = reh.extract_print_str(item['printed'])
                item['last_tracking'] = reh.extract_replace_str(item['last_tracking'])
                item['created'] = tf.format_timestamp(item['created'])
                item['picking_time'] = tf.format_timestamp(item['picking_time'])
                item['delivered_time'] = tf.format_timestamp(item['delivered_time'])
                item["logistics_state"] = shipped_status
            return page_dataSource
        except Exception as e:
            logger.warning(f"处理数据Error: {e}")

    def fetch_all_data(self, shipped_status: str, total_pages: int):
        """顺序获取所有页的数据"""
        page_data = []
        for page in range(1, total_pages + 1):
            try:
                page_data = self.fetch_page_data(shipped_status, page)
                if shipped_status == "all" and page_data:
                    # view页面的采集：
                    basecrawlerview = BaseCrawlerView(page_data)
                    view_list_id = basecrawlerview.get_viewid()
                    # url的id信息列表放入队列中
                    self.view_id_data_queue.put(view_list_id)
            except Exception as e:
                logger.error(f'------- 任务执行中发生了异常: {e} -------')

            self.data_queue.put((shipped_status, page_data))  # 将数据放入队列

    def process_data_from_queue(self):
        """从队列中获取数据并处理"""
        while not self.data_queue.empty():
            data = self.data_queue.get()

            try:
                shipped_status, page_data = data
                if not page_data:
                    break
                processed_data_all = self.process_data(page_data, shipped_status)
                # 只有当 'shipment_id' 字段包含 'FBA'、'OWS' 或 'GDM' 中的任何一个时，元素才会被添加到 processed_data 列表
                processed_data = [d for d in processed_data_all if
                                 any(substring in d['shipment_id'] for substring in ['FBA', 'OWS', 'GDM'])]
                # 配置文件中setting数据库表的字段列表,并且将数据三元组放入插入消费者队列中
                self.insert_data_queue.put((self.db_table,
                                            self.table_field_list,
                                            processed_data))
            except Exception as ex:
                logger.info(f"Error processing data: {ex}")

    def insert_data_to_db_from_queue(self):
        """缓冲区：从队列中获取数据并批量插入到数据库"""
        buffer = []
        # time.time(): 返回当前的时间戳（从1970年1月1日00:00:00 UTC到现在的秒数）
        last_insert_time = time.time()
        # 队列为空或超时,抛出queue.Empty异常
        while not self.insert_data_queue.empty():
            try:
                # 队列在 self.insert_interval 秒内没有新的数据可获取，get 方法将抛出 queue.Empty 异常,超时行为
                data = self.insert_data_queue.get(timeout=self.insert_interval)
                # 列表中添加元素-->a:[1, 2, 3] b:[4, 5] a.append(b):[1, 2, 3, [4, 5]]  extend:[1, 2, 3, 4, 5]
                buffer.append(data)

                # 如果缓冲区达到批量大小，插入数据
                if len(buffer) >= self.batch_size:
                    # print(len(buffer))
                    self.bulk_insert(buffer)
                    buffer = []
                    last_insert_time = time.time()
            # 异常类:队列为空且在指定的超时时间内没有获取到数据时被抛出
            except queue.Empty:
                # 如果达到插入间隔时间，插入数据
                if buffer and (time.time() - last_insert_time >= self.insert_interval):
                    self.bulk_insert(buffer)
                    buffer = []
                    last_insert_time = time.time()
            except Exception as ex:
                print(f"Error inserting data to db: {ex}")

        # 插入剩余的数据
        if buffer:
            self.bulk_insert(buffer)

    def bulk_insert(self, buffer):
        """缓冲区：批量插入数据到数据库"""
        try:
            # 三元组中第一个数据项的第一个元素(db_table, field_list, processed_data)：db_table
            db_table = buffer[0][0]
            # 第一个数据项的第二个元素：field_list (buffer[0]：缓冲区中的第一个数据项)
            field_list = buffer[0][1]
            # 列表推导式-->从buffer循环出三元组，再从元组的第三个元素，循环出里面的字典，最后放在data_list列表中--> processed_data
            data_list = [list_item for tup in buffer for list_item in tup[2]]
            self.insert_data_to_db(db_table, field_list, data_list)
        except Exception as ex:
            print(f"Error in bulk insert: {ex}")

    def insert_data_to_db(self, db_table: str, field_list: list, data_list: [dict]):
        """创建和插入数据到数据库"""
        # with 语句结合上下文管理器模式:使用 DatabaseConnector 并且确保事务管理
        with DatabaseConnector() as db_connector:
            connection = db_connector.connection
            # with 语句结合上下文管理器模式:默认情况下，许多数据库连接库（包括 pymysql）在连接时会自动开启一个事务
            with connection.cursor() as cursor:
                sql_string_tuple = list_to_sql_values(field_list, data_list)
                cursor.execute(self.create_table_query)
                insert_sql = create_insert_sql(db_table, field_list,
                                               sql_string_tuple)
                cursor.execute(insert_sql)

    @RetryDecorator.retry(max_attempts=3)
    @RetryDecorator.retry_decorator(msg="采集数据出错", error_type=713, max_retry_count=3, time_interval=1)
    def fetch_view_each(self, view_id: str):
        """获取指定id的view页的数据"""
        params = {
            'id': view_id,
        }
        response = self.session.get(self.view_url, params=params)
        if response.status_code != 200:
            return {}
        row_data = response.json()
        row_data['view_id'] = view_id
        if row_data['success'] == 0:
            print(view_id, self.view_url, self.logistics_provider_code)
            return None
        return row_data

    def fetch_view_data(self, ):
        """顺序获取每一页主数据中传入的id详情页的数据"""
        # while not self.view_id_data_queue.empty():
        #     view_list_id = self.view_id_data_queue.get()
        sql = f"SELECT id FROM `ods_prod`.`ods_scg_wld_logistics_trace_table_i_d` WHERE logistics_state = 'all' " \
              f"AND logistics_provider = '{self.logistics_provider}' " \
              f"AND dt >= DATE_FORMAT('{self.start_date}','%Y%m%d')"
        view_list_dict = self.tidb.query_list(sql)
        view_list_id = [item['id'] for item in view_list_dict]
        for view_id in view_list_id:
            try:
                view_data = self.fetch_view_each(view_id)
                if view_data is not None:
                    self.view_data_queue.put(view_data)
            except Exception as e:
                logger.error(f'------- 任务执行中发生了异常: {e} -------')

    def process_view_data(self, view_data: dict):
        """处理每个id对应的详情页面数据"""
        view_id = ''
        shipment_id = ''
        status_list = []
        result = []
        try:
            view_id = view_data['view_id']
            shipment_id = \
                view_data['data']['rows'][1]['components'][1]['data']['body']['components'][1]['data']['columns'][0][
                    'data'][0]['data']['value']
            status_list = jsonpath(view_data,
                                   "$..[?(@.comKey=='tms-csos-shipment-tracking')]..['dataSource'].['title','info']")
        except Exception as e:
            logger.warning(f"处理数据Error: {e}")
        if self.logistics_provider == '东方环球物流':
            result = BaseCrawlerView.extract_ges_view_info(view_id, self.logistics_provider, shipment_id, status_list)
        elif self.logistics_provider == '澳得亚物流':
            result = BaseCrawlerView.extract_auasian_view_info(view_id, self.logistics_provider, shipment_id,
                                                               status_list)
        elif self.logistics_provider == '美通物流':
            result = BaseCrawlerView.extract_aaf_view_info(view_id, self.logistics_provider, shipment_id, status_list)
        else:
            logger.info(f'详情页面数据处理错误')
        return result

    def process_view_from_queue(self):
        while not self.view_data_queue.empty():
            view_data = self.view_data_queue.get()
            if not view_data:
                break
            processed_view_data = self.process_view_data(view_data)
            self.detail_page_data.extend(processed_view_data)

    def insert_viewdata_to_db(self, db_table: str, field_list: list, sql_string_tuple: [tuple]):
        """创建和插入view数据到数据库"""
        # with 语句结合上下文管理器模式:使用 DatabaseConnector 并且确保事务管理
        with DatabaseConnector() as db_connector:
            connection = db_connector.connection
            with connection.cursor() as cursor:
                cursor.execute(self.create_view_query)
                sql_values = ', '.join(str(values) for values in sql_string_tuple)
                insert_sql = create_insert_sql(db_table, field_list,
                                               sql_values)
                cursor.execute(insert_sql)

    def del_logistics_data(self):
        """
        清空 ahc 近 3个月的数据
        订单起始时间 和终止时间  后台筛选存在问题
        :return:
        """
        sql_table = f"delete from ods_prod.ods_scg_wld_logistics_trace_table_i_d WHERE dt >= DATE_FORMAT('{self.start_date}','%Y%m%d') "
        self.tidb.commit_sql(sql_table)
        sql_view = f"delete from ods_prod.ods_scg_wld_logistics_trace_view_i_d WHERE DATE_FORMAT(created,'%Y%m%d') >= DATE_FORMAT('{self.start_date}','%Y%m%d') "
        self.tidb.commit_sql(sql_view)
        logger.info("删除东方环球、澳得亚物流、美通物流数据 180天成功")

    def run_producer_consumer(self, shipped_status, total_pages):
        # 主页面数据 生产者
        self.fetch_all_data(shipped_status, total_pages)
        # 处理
        self.process_data_from_queue()
        # 插入
        self.insert_data_to_db_from_queue()

    def run_view(self):
        # 拿每页的id，requests数据。
        self.fetch_view_data()

        # 处理
        self.process_view_from_queue()

        # 插入
        self.insert_viewdata_to_db(self.db_view, self.view_field_list, self.detail_page_data)

    def run(self):
        """生产消费者模式采集流程"""

        start_time_ = time.time()

        # Redis 中获取并设置到 headers 中
        self.session.headers['token'] = self.get_auth_token()

        # 必须等主页面数据完全跑完之后，再去数据库中拿不包含已取消的id数据，采集详情页面的信息。
        type_list = ["all", "cancelled"]
        for shipped_status in type_list:
            try:
                # 获取指定页的数据，用于总行数和页数.
                initial_response = self.fetch_page_data(shipped_status=shipped_status)
                total_pages = self.get_total_pages(initial_response)

                if total_pages == 0:
                    continue

                self.run_producer_consumer(shipped_status, total_pages)
                logger.info(f'当前主页面数据采集： {self.logistics_provider} {shipped_status} 采集完成.')

                # if shipped_status != "cancelled":
            except Exception as e:
                logger.error(f"{self.logistics_provider}处理主页面数据 {shipped_status} 状态时发生错误: {e}")
        try:
            self.run_view()
            logger.info(f'当前详情页面数据采集： {self.logistics_provider} 不包含已取消数据 采集完成.')
        except Exception as e:
            logger.error(f"{self.logistics_provider}处理详情页面数据时发生错误: {e}")

        logger.info(f'程序.Time: {time.time() - start_time_:.2f}s')

    def main(self):
        self.del_logistics_data()
        logistics_provider_list = ["GES", "AUASIAN", "AAF"]
        # logistics_provider_list = ["AUASIAN"]
        for logistics_provider in logistics_provider_list:
            self.init_logistic(logistics_provider)
            self.run()


if __name__ == "__main__":
    # 创建 LogisticsDataFetcher_nextsls 类的一个实例 fetcher
    fetcher = LogisticsDataFetcher_nextsls()
    # 调用 fetcher 的 run 方法开始执行数据抓取任务
    fetcher.main()
