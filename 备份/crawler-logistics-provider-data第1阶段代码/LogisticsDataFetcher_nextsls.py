# -*- coding: utf-8 -*-
# @Time    : 2024/8/9 15:34
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:

import requests
import queue
import threading
import time

from crawler_base import BaseCrawler
from method import TimestampFormatter, RegularExpressionHtml, \
    DatabaseConnector, list_to_sql_values, create_insert_sql, \
    RetryDecorator, init_redis, BaseCrawlerView
from datetime import datetime
import concurrent.futures
import configparser
from loguru import logger
from jsonpath import jsonpath

"""
    requests：用于发送HTTP请求。
    redis：用于与Redis数据库交互。
    logistics_init.Dao：假设是自定义模块，包含一些工具类和数据库连接类。
    datetime：用于处理日期和时间。
    concurrent.futures：用于并发执行任务，特别是线程池
    configparser:用于读取和编写配置文件
    loguru:记录各种信息，包括调试信息、错误信息等
    json:序列化将Python对象转换为JSON字符串 和反序列化（将JSON字符串转换为Python对象）
    import queue : 是 Python 中的一个导入语句，用于导入标准库中的 queue 模块。queue 模块包含了几种队列类，
    如 Queue、PriorityQueue 和 LifoQueue。在这个例子中，我们使用 Queue 类创建了一个队列，用于在生产者和消费者线程之间传递数据.
    import threading：是一个 Python 的导入语句，用于导入标准库中的 threading 模块。threading 模块用于创建和管理线程，是 Python 中实现多线程编程的主要模块。
    import time:处理时间相关的操作.例time.sleep(seconds) 来让当前线程暂停指定的秒数,time.time() 来获取当前的 Unix 时间戳.
    jsonpath:是一个 Python 库，它提供了一种在 Python 中查询 JSON 文档的方式。这种查询方式的语法与 XPath 查询 XML 文档的语法类似，但是用于处理 JSON。
    # 1.发送 HTTP 请求：支持各种 HTTP 方法，如 GET、POST、PUT、DELETE、HEAD、OPTIONS 等。
    # 2.处理响应：能够轻松处理服务器返回的响应，包括获取响应状态码、响应头和响应内容。
    # 3.处理 URL 参数：能够方便地处理查询参数和 URL 编码。
    # 4.会话管理：支持会话对象，可以在多个请求之间保持会话（例如，保持 cookies）。
    # 5.文件上传：支持文件上传。
    # 6.认证：支持多种认证方式，如基本认证、OAuth 等。
    # 7.超时和重试：可以设置请求的超时时间和重试策略。
"""

config = configparser.ConfigParser()
config.read(r'.\config.ini', encoding='utf-8')


class LogisticsDataFetcher_nextsls(BaseCrawler):
    """可以继承其他class，使用self调用."""

    def __init__(self):
        """定义 LogisticsDataFetcher 类"""
        super().__init__()
        # 创建了主页面一个队列，这个队列用于在生产者（数据抓取线程）和消费者（数据处理线程）之间传递数据。队列是线程安全的，可以在多线程环境下进行操作。
        self.data_queue = queue.Queue()
        # 创建采集view详情页面的url数据队列。
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
        self.detail_page_data = []


    @RetryDecorator.retry_decorator(msg="采集数据出错", error_type=713, max_retry_count=3, time_interval=1)
    def fetch_page_data(self, shipped_status: str, page=1):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""
        # try:
        fetch_json_data = {
            'timeLimit': 0,
            'page': page,
            'activeTab': shipped_status,
            'isActiveTab': 'all',
            'scenes': 1,
        }
        """
        发送 POST 请求获取指定页的数据。
        若请求成功，返回 JSON 响应。
        若请求失败或 JSON 解析失败，捕获异常并返回 None。
        """
        response = self.session.post(self.data_url, json=fetch_json_data)
        response.raise_for_status()
        return response.json()
        """
        需要装饰器重试就不能捕获异常：
        # # 处理由 requests 库引发的各种请求相关问题，如网络连接问题、超时、无效的响应等
        # except requests.exceptions.RequestException as requests_e:
        #     print(f"Request failed for page {page}: {requests_e}")
        #     return None
        # # 捕获 JSON 解码相关的错误
        # except json.JSONDecodeError as json_ex:
        #     print(f"Failed to parse JSON for page {page}: {json_ex}")
        #     return None
        """

    @RetryDecorator.retry(max_attempts=3)
    @RetryDecorator.retry_decorator(msg="采集数据出错", error_type=713, max_retry_count=3, time_interval=1)
    def fetch_view_each(self, view_id: str):
        """获取指定id的view页的数据"""
        params = {
            'id': view_id,
        }
        response = self.session.get(self.view_url, params=params)
        response.raise_for_status()
        row_data = response.json()
        row_data['view_id'] = view_id
        if row_data['success'] == 0:
            print(view_id, self.view_url, self.logistics_provider_code)
            return None
        return row_data

    def get_total_pages(self, data_dict: dict):
        """
        根据响应数据获取分页信息
        :param data_dict: 初始响应数据
        :return: 总页数
        """
        # 获取总行数（total_rows）和每页的大小（page_size）
        total_rows = data_dict['data']['components']['gridView']['table']['pagination']['total']
        page_size = data_dict['data']['components']['gridView']['table']['pagination']['pageSize']

        # 将总行数加上每页大小减一,然后整除每页大小来完成的.这样做是为了确保如果总行数不能被每页大小整除时,总页数会向上取整.
        total_pages = (total_rows + page_size - 1) // page_size

        return total_pages

    def process_data(self, page_data: dict, shipped_status: str):
        """处理每页的数据"""
        try:
            if 'data' in page_data and 'components' in page_data['data']:
                page_dataSource = page_data['data']['components']['gridView']['table']['dataSource']
                # 添加当前时间 2024-07-31 17:37:01.038610
                current_time = datetime.now().strftime('%Y%m%d')
                for item in page_dataSource:
                    item["dt"] = current_time
                    item['logistics_provider'] = self.logistics_provider
                    item['shipment_id'] = RegularExpressionHtml.extract_logistics_codes(item['shipment_id'])
                    item['to_address_country'] = RegularExpressionHtml.extract_replace_str(item['to_address_country'])
                    item['parcel_count'] = RegularExpressionHtml.extract_html_font(item['parcel_count'])
                    item['actual_weight'] = RegularExpressionHtml.extract_html_font(item['actual_weight'])
                    # 　get() 方法接受两个参数：键和默认值。如果字典中存在这个键，get() 方法会返回这个键对应的值；如果字典中不存在这个键，get() 方法会返回默认值。
                    item['actual_volume'] = RegularExpressionHtml.extract_html_font(item.get('actual_volume', 'None'))
                    item['actual_volume_weight'] = RegularExpressionHtml.extract_html_font(item['actual_volume_weight'])
                    item['exportwith'] = RegularExpressionHtml.extract_html_sapn(item['exportwith'])
                    item['outer_carrier'] = RegularExpressionHtml.extract_html_info(item['outer_carrier'])
                    item['printed'] = RegularExpressionHtml.extract_print_str(item['printed'])
                    item['last_tracking'] = RegularExpressionHtml.extract_replace_str(item['last_tracking'])
                    item['created'] = TimestampFormatter.format_timestamp(item['created'])
                    item['picking_time'] = TimestampFormatter.format_timestamp(item['picking_time'])
                    item['delivered_time'] = TimestampFormatter.format_timestamp(item['delivered_time'])
                    item["logistics_state"] = shipped_status
                return page_dataSource
            else:
                print(
                    f"Unexpected data format for page {page_data['data']['components']['gridView']['table']['pagination']['page']}")
        # KeyError异常：通常在尝试访问字典中不存在的键时引发
        except KeyError as e:
            print(f"KeyError: {e}")
            return []

    def fetch_all_data(self, shipped_status: str, total_pages: int):
        """并发获取所有页的数据"""
        try:
            # 使用多线程获取所有页的数据:创建线程池:使用 ThreadPoolExecutor 创建一个包含 4 个线程的线程池
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                """
                使用列表推导式生成一个任务列表 futures，每个任务都是调用 fetch_page_data 函数获取特定页码的数据。
                executor.submit(self.fetch_page_data, shipped_status, page) 提交任务到线程池，
                page 从 2 到 total_pages（因为第一页已经获取）,左闭右开.
                """
                # 如果total_pages=1，[2,2),会返回一个空列表
                futures = [executor.submit(self.fetch_page_data, shipped_status, page) for page in
                           range(1, total_pages + 1)]
                # 使用 concurrent.futures.as_completed(futures) 遍历已完成的任务
                for future in concurrent.futures.as_completed(futures):
                    # 对于每个已完成的任务，调用 future.result() 获取任务的返回值（即页面数据）
                    page_data = future.result()
                    if shipped_status == "all":
                        # view页面的采集：
                        basecrawlerview = BaseCrawlerView(page_data)
                        view_list_id = basecrawlerview.get_viewid()
                        # url的id信息列表放入队列中
                        self.view_id_data_queue.put(view_list_id)

                    # page = page_data['data']['components']['gridView']['table']['pagination']['page']
                    # logger.info(f'当前采集 {self.logistics_provider} {shipped_status} {page} ')
                    if page_data:
                        # page_data: dict  返回列表套字典.
                        self.data_queue.put((shipped_status, page_data))  # 将数据放入队列
        except Exception as ex:
            # 增加异常处理，以及更加详细的日志记录
            print(f"Error fetching data for a page: {ex}")
        # # 格式：列表套字典

    def fetch_view_data(self, ):
        """并发获取每一页主数据中传入的id详情页的数据"""
        try:
            while True:
                # 队列为空，跳出循环
                if self.view_id_data_queue.empty():
                    break
                view_list_id = self.view_id_data_queue.get()

                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    futures = [executor.submit(self.fetch_view_each, view_id) for view_id in view_list_id]
                    for future in concurrent.futures.as_completed(futures):
                        # 对于每个已完成的任务，调用 future.result() 获取任务的返回值（即页面数据）
                        view_data = future.result()
                        if view_data is None:
                            continue
                        self.view_data_queue.put(view_data)
        except Exception as ex:
            # 增加异常处理，以及更加详细的日志记录
            print(f"Error view fetching : {ex}")

    def process_data_from_queue(self):
        """从队列中获取数据并处理"""
        while True:
            """
            self.data_queue.get() 是从队列 self.data_queue 中取出一个元素。在 Python 的 queue 库中，
            get() 方法用于从队列中删除并返回一个元素。如果队列为空，get() 方法会阻塞，直到有元素被放入队列。得到的元素被赋值给 page_data。
            这里的 self.data_queue 是一个队列对象，可能在类的其他部分被初始化。队列是一种先进先出（FIFO）的数据结构，
            可以用来在多线程或多进程环境下安全地从一个线程或进程传递数据到另一个线程或进程。
            """
            if self.data_queue.empty():
                break
            page_data = self.data_queue.get()
            """
            数据以二元元组(shipped_status, page_data)的形式放入队列。当你从队列中get()数据时，返回的就是这个元组。那么，shipped_status, page_data = page_data
            这句代码就是将元组中两个元素分别赋值给shipped_status和page_data。这个操作叫做解构（或解包）。
            """
            try:
                shipped_status, page_data = page_data
                processed_data = self.process_data(page_data, shipped_status)
                # page = page_data['data']['components']['gridView']['table']['pagination']['page']
                """
                1、logger: 这是一个 Python 中的日志记录器对象，通常是通过 Python 的内置 logging 模块创建的。日志记录器用于控制日志消息的输出方式和级别。
                2、.info(): 这是日志记录器对象的一个方法，用于记录信息级别的日志消息。信息级别通常用于输出程序的一般信息，表示程序在正常运行中的一些重要信息。
                3、f'当前采集 {shipped_status} {len(all_data)} 采集完成': 这是一个格式化字符串（f-string）
                """
                # logger.info(
                #     f'当前处理 {self.logistics_provider} {shipped_status} 第{page}页 总计{len(processed_data)}采集完成')
                if processed_data:
                    # 配置文件中setting数据库表的字段列表,并且将数据三元组放入插入消费者队列中
                    self.insert_data_queue.put((self.db_table,
                                                self.table_field_list,
                                                processed_data))
            except Exception as ex:
                print(f"Error processing data: {ex}")

    def process_view_from_queue(self):
        while True:
            if self.view_data_queue.empty():
                break
            view_data = self.view_data_queue.get()
            processed_view_data = self.process_view_data(view_data)
            self.detail_page_data.extend(processed_view_data)

    def process_view_data(self, view_data: dict):
        """处理每个id对应的详情页面数据"""
        """
        * ：该节点下面所有
        . :选择当前对象的子元素  JSON 对象 { "name": "John" }，你可以使用表达式 $.name 来选择 "name" 字段的值
        .. :递归下降运算符,它用于选择当前对象和所有子元素中的元素.套的 JSON 对象 { "person": { "name": "John" } }，你可以使用表达式 $..name 来选择 "name" 字段的值，无论它在对象的哪一层
        """
        result = []
        id = view_data['view_id']
        shipment_id = \
        view_data['data']['rows'][1]['components'][1]['data']['body']['components'][1]['data']['columns'][0][
            'data'][0]['data']['value']
        status_list = jsonpath(view_data,
                               "$..[?(@.comKey=='tms-csos-shipment-tracking')]..['dataSource'].['title','info']")
        if self.logistics_provider == '东方环球物流':
            result = BaseCrawlerView.extract_ges_view_info(id, self.logistics_provider, shipment_id, status_list)
        elif self.logistics_provider == '澳得亚物流':
            result = BaseCrawlerView.extract_auasian_view_info(id, self.logistics_provider, shipment_id, status_list)
        elif self.logistics_provider == '美通物流':
            result = BaseCrawlerView.extract_aaf_view_info(id, self.logistics_provider, shipment_id, status_list)
        else:
            logger.info(f'详情页面数据处理错误')
        return result

    def insert_data_to_db_from_queue(self):
        """缓冲区：从队列中获取数据并批量插入到数据库"""
        buffer = []
        # time.time(): 返回当前的时间戳（从1970年1月1日00:00:00 UTC到现在的秒数）
        last_insert_time = time.time()
        while True:
            try:
                # 队列为空或超时,抛出queue.Empty异常
                if self.insert_data_queue.empty():
                    break
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

        """
        1、在 while 循环中,批量插入操作是由缓冲区大小或时间间隔触发的.
        2、当循环结束时,可能缓冲区中的数据量还没有达到 batch_size，或者时间间隔还没有到达 insert_interval.
        3、为了确保所有数据都能被插入到数据库中,循环结束后需要检查缓冲区中是否还有剩余的数据,并进行插入.
        """
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
        # 使用 DatabaseConnector 并且确保事务管理
        try:
            # with 语句结合上下文管理器模式
            with DatabaseConnector(host=config['Database']['host'], port=int(config['Database']['port']),
                                   user=config['Database']['user'], password=config['Database']['password'],
                                   database=config['Database']['database']) as db_connector:
                connection = db_connector.connection
                with connection.cursor() as cursor:
                    cursor.execute("BEGIN")
                    sql_string_tuple = list_to_sql_values(field_list, data_list)
                    cursor.execute(self.create_table_query)
                    insert_sql = create_insert_sql(db_table, field_list,
                                                   sql_string_tuple)
                    cursor.execute(insert_sql)
                    # logger.info(f'插入完成')
        except Exception as e:
            print(f"操作失败: {e}")

    def insert_viewdata_to_db(self, db_table: str, field_list: list, sql_string_tuple: [tuple]):
        """创建和插入数据到数据库"""
        # 使用 DatabaseConnector 并且确保事务管理
        try:
            # with 语句结合上下文管理器模式
            with DatabaseConnector(host=config['Database']['host'], port=int(config['Database']['port']),
                                   user=config['Database']['user'], password=config['Database']['password'],
                                   database=config['Database']['database']) as db_connector:
                connection = db_connector.connection
                with connection.cursor() as cursor:
                    cursor.execute("BEGIN")
                    cursor.execute(self.create_view_query)
                    sql_values = ', '.join(str(values) for values in sql_string_tuple)
                    insert_sql = create_insert_sql(db_table, field_list,
                                                   sql_values)
                    cursor.execute(insert_sql)
                    # logger.info(f'插入完成')
        except Exception as e:
            print(f"操作失败: {e}")

    def run(self):
        """生产消费者模式采集流程"""
        start_time = time.time()
        start_time_ = time.time()

        # Redis 中获取并设置到 headers 中
        self.session.headers['token'] = self.get_auth_token()
        # 六个tab页的activeTab键值.
        # type_list = ["ready", "picked", "in_transit", "delivered", "returned", "cancelled"]
        type_list = ["all", "cancelled"]
        for shipped_status in type_list:

            # 获取指定页的数据，用于总行数和页数.
            initial_response = self.fetch_page_data(shipped_status=shipped_status)
            total_pages = self.get_total_pages(initial_response)

            if total_pages == 0:
                continue

            # 创建主页面生产者线程
            # 创建了一个新的线程,该线程的目标函数是 self.fetch_all_data,并将 shipped_status 和 total_pages 作为参数传递给这个函数.线程被启动.
            producer_thread = threading.Thread(target=self.fetch_all_data, args=(shipped_status, total_pages))
            producer_thread.start()

            # 等待生产者线程结束:阻塞当前线程,直到生产者线程结束.
            producer_thread.join()

            # 创建消费者线程： 列表推导式来创建四个消费者线程,遍历列表，循环启动四个线程.(利用多核 CPU 的有效方式)
            consumer_threads = [threading.Thread(target=self.process_data_from_queue) for _ in
                                range(4)]
            for thread in consumer_threads:
                thread.start()

            # 等待消费者线程结束:遍历线程,阻塞当前线程,直到所有的消费者线程都结束.
            for thread in consumer_threads:
                thread.join()

            # 创建插入数据到数据库线程
            db_insert_thread = threading.Thread(target=self.insert_data_to_db_from_queue)
            db_insert_thread.start()

            # 等待插入数据的线程结束
            db_insert_thread.join()

            logger.info(
                f'当前主页面数据采集 {self.logistics_provider} {shipped_status} 采集完成.Time: {time.time() - start_time:.2f}s')
            start_time = time.time()

            if shipped_status == "cancelled":
                continue

            # 创建view页面生产者线程：四个线程去拿每页的id，requests数据。
            viewproducer_threads = [threading.Thread(target=self.fetch_view_data) for _ in
                                    range(4)]
            for thread in viewproducer_threads:
                thread.start()

            # 等待view生产者线程结束
            for thread in viewproducer_threads:
                thread.join()

            # 创建view消费者线程
            viewconsumer_threads = [threading.Thread(target=self.process_view_from_queue) for _ in
                                    range(4)]
            for thread in viewconsumer_threads:
                thread.start()

            # 等待view消费者者线程结束
            for thread in viewconsumer_threads:
                thread.join()

            self.insert_viewdata_to_db(self.db_view, self.view_field_list, self.detail_page_data)
            logger.info(
                f'当前view数据采集 {self.logistics_provider} {shipped_status}.Time: {time.time() - start_time:.2f}s')
            start_time = time.time()

        logger.info(f'程序.Time: {time.time() - start_time_:.2f}s')

    def main(self):

        # with 语句结合上下文管理器模式
        with DatabaseConnector(host=config['Database']['host'], port=int(config['Database']['port']),
                               user=config['Database']['user'], password=config['Database']['password'],
                               database=config['Database']['database']) as db_connector:
            connection = db_connector.connection
            with connection.cursor() as cursor:
                cursor.execute("BEGIN")
                cursor.execute("TRUNCATE TABLE ods_prod.ods_scg_wld_logistics_trace_table_i_d")
                cursor.execute("TRUNCATE TABLE ods_prod.ods_scg_wld_logistics_trace_view_i_d")

        logistics_provider_list = ["GES", "AUASIAN", "AAF"]
        # logistics_provider_list = ["GES"]
        for logistics_provider in logistics_provider_list:
            # 创建 LogisticsDataFetcher_nextsls 类的一个实例 fetcher
            self.init_logistic(logistics_provider)
            # 调用 fetcher 的 run 方法开始执行数据抓取任务
            self.run()


if __name__ == "__main__":
    # 创建 LogisticsDataFetcher_nextsls 类的一个实例 fetcher
    fetcher = LogisticsDataFetcher_nextsls()
    # 调用 fetcher 的 run 方法开始执行数据抓取任务
    fetcher.main()
