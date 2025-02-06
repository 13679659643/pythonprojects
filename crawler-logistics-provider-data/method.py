# -*- coding: utf-8 -*-
# @Time    : 2024/8/1 11:45
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:共用方法
"""
1、import json: 导入 Python 的 json 模块，用于处理 JSON 数据。
2、import time: 导入 Python 的 time 模块，用于处理时间相关的操作。
3、from collections import OrderedDict: 从 collections 模块导入 OrderedDict 类，这是一个字典子类，它记住了元素添加的顺序。
4、from functools import wraps: 从 functools 模块导入 wraps 函数，常用于装饰器定义，用来保留原函数的元信息（如函数名、注释等）。
5、import pymysql: 导入 pymysql 包，这是一个 Python MySQL 客户端库，用于连接和操作 MySQL 数据库。
6、import re: 导入 Python 的 re 模块，用于处理正则表达式。
7、from pymysql import MySQLError: 从 pymysql 包导入 MySQLError 类，这是一个用于处理 MySQL 错误的异常类。
8、from datetime import datetime: 从 datetime 模块导入 datetime 类，用于处理日期和时间。
9、from loguru import logger: 从 loguru 包导入 logger，这是一个用于记录日志的工具。
"""
import json
import logging
import time
from collections import OrderedDict
from functools import wraps
import pymysql
import re
import configparser
import redis
from pymysql import MySQLError
from datetime import datetime
from loguru import logger
from digiCore.db.redis.core import RedisDao
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, './config.ini')


def format_error_msg(e):
    """
    日志输出所在的文件路径、行号、具体错误信息。
    :param e:
    :return:
    """
    # 这一行代码获取了错误发生时所在的文件名,并使用 logger.error() 方法将其记录到日志中.
    logger.error(f'错误文件路径:{e.__traceback__.tb_frame.f_globals["__file__"]}')
    # 获取错误所在的行号.
    logger.error(f'代码错误行位置:{e.__traceback__.tb_lineno}')
    # 这一行代码获取了错误的消息内容,并使用 logger.error() 方法将其记录到日志中.e.args 通常包含了错误的具体信息或描述.
    logger.error(f'错误信息:{e.args}')


class RetryDecorator:
    @classmethod
    def retry_decorator(cls, msg=None, error_type=None, max_retry_count: int = 5, time_interval: int = 2):
        """
        任务重试装饰器
        msg:错误信息
        error_type：错误类型
        max_retry_count: 最大重试次数 默认5次
        time_interval: 每次重试间隔 默认2s
        @RetryDecorator.retry_decorator(msg="存放错误信息的位置", error_type=713, max_retry_count=3, time_interval=1)
        def my_function():
            a = 1
            b = json.loads(a)
            print(b)
            print(type(b))
            return b
        """

        def _retry(func):
            # 保留原始函数的元数据（如函数名、文档字符串、参数列表等）
            @wraps(func)
            def wrapper(*args, **kwargs):
                for retry_count in range(max_retry_count):
                    try:
                        """
                        *args 和 **kwargs 是 Python 中的惯例写法，用于处理函数定义中的可变数量的位置参数和关键字参数:
                        *args：这个写法表示接受任意数量的位置参数，并将它们作为一个元组传递给函数。在函数内部，可以通过 args 这个元组来访问这些位置参数。
                        **kwargs：这个写法表示接受任意数量的关键字参数，将它们作为一个字典传递给函数。在函数内部，可以通过 kwargs 这个字典来访问这些关键字参数。
                        """
                        task_result = func(*args, **kwargs)
                        return task_result

                    except Exception as e:
                        logger.error(msg if msg else f"{max_retry_count}： 函数报错，正在重试！")
                        format_error_msg(e)
                        time.sleep(time_interval)
                # 如果超过最大重试次数仍未成功,则返回指定的错误类型或默认值.
                return logger.error(error_type) if error_type else f"超过最大重试次数仍未成功！"

            # 装饰器的必要结构：返回了包装原始函数的函数,实现了在函数执行前后添加额外逻辑的功能.
            return wrapper

        # 返回了装饰器函数,使得外部可以通过 @Decorate.def_retry() 的方式来调用这个装饰器.
        return _retry

    @classmethod
    def retry(cls, max_attempts: int = 3):
        """
            装饰器，用于重试指定次数
            :param max_attempts: 最大重试次数
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                attempts = 0
                while attempts < max_attempts:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                    attempts += 1
                    logger.warning(f"尝试第 {attempts} 次失败，重新尝试...")
                    time.sleep(1)  # 可选：添加延迟避免频繁请求
                logger.error(f"超过最大重试次数 {max_attempts} 次，操作失败")
                return None

            return wrapper

        return decorator


# 正则表达式封装html函数
class RegularExpressionHtml:
    # 按 "<br/>" 分割、提取正则表达式 >[^<]+部分：从>开始到>结束.
    @staticmethod
    def extract_logistics_codes(html):
        """
        正则表达式 `>[^<]+` 的含义如下：
        - `>`：匹配字符 `>`。在 HTML 中，`>` 通常用来结束一个标签。
        - `[^<]+`：匹配一串不包含 `<` 的字符。`[^<]` 的含义是匹配任何不是 `<` 的字符，`+` 的含义是匹配前面的字符一次或多次。所以 `[^<]+`
        的含义是匹配一串不包含 `<` 的字符，直到遇到 `<` 为止。
        所以，整个正则表达式 `>[^<]+` 的含义是匹配从 `>` 开始，到下一个 `<` 之前的所有字符。在 HTML 中，这通常对应一个标签内的文本。例如，
        在字符串 `<tag>text</tag>` 中，`>[^<]+` 将匹配 `>text`。
        请注意，这个正则表达式返回的匹配结果会包含开始的 `>` 字符，所以在代码中使用 `[1:]` 来获取 `>` 后面的文本。
        <br：
        匹配字符串 <br，即 HTML 标签的开头部分。
        \s*：
        \s 匹配任意空白字符，包括空格、制表符和换行符。
        * 是量词，表示匹配前面的元素 0 次或多次。
        因此，\s* 匹配 0 个或多个空白字符。这个部分允许 <br> 标签和可能存在的空白字符之间的容忍度。
        \/?：
        \/ 匹配字符 /。因为 / 是正则表达式中的特殊字符，所以需要使用反斜杠 \ 进行转义。
        ? 是量词，表示匹配前面的元素 0 次或 1 次。
        因此，\/? 匹配 0 次或 1 次 /。这个部分允许 <br> 标签在自闭合形式 <br/> 和非自闭合形式 <br> 之间的容忍度。
        >：
        匹配字符 >，即 HTML 标签的结束部分。
        :param html:4179484GDM-7690026776、4179484GDM/7690026776、PL-LM20240530-1/7600008134、4179484GDM
        IN20240816094210+一件代发 五种格式
        :return:
        """
        # 匹配 HTML 中的 <br> 标签
        pattern = r'<br\s*\/?>'
        # 将输入字符串按 "<br/>" 分割,结果是一个列表，列表的每个元素都是一个字符串.
        parts = re.split(pattern, html)
        # 创建了一个空列表,用于存储每一部分的最后一个标签内的文本
        last_logistics_codes = []
        dropshipping_logistics_codes = ''
        for part in parts[1:]:
            # 正则表达式 >[^<]+ 在每一部分中查找所有的标签内的文本。结果是一个列表，列表的每个元素都是一个匹配的字符串。
            matches = re.findall(r'>[^<]+', part)
            # 如果找到匹配项，则取最后一个匹配项
            if matches:
                # matches[-1] 是获取 matches 列表的最后一个元素，[1:] 是获取这个元素从第二个字符开始到最后的部分
                match = matches[-1][1:]
                # 检查字符串是否只包含英文字符和数字  ^：开始 $：结束  (?=.*[A-Za-z])：前瞻断言，任意数量的任意字符后面跟着一个英文字母.
                # (?=.*[0-9])：任意数量的任意字符后面跟着一个数字.  [A-Za-z0-9]+：任意数量（至少一次）的英文字母（无论大小写）或数字。
                if re.match(r'^(?=.*[A-Za-z])(?=.*[0-9])[A-Za-z0-9]+$', match):
                    # 匹配的字符串添加到 last_logistics_codes 列表中
                    last_logistics_codes.append(match)
                else:
                    if '/' in match:
                        # 转义’\/‘:re.split(r'\/|-', match) 将字符串 match 按照 \/ 或者 - 进行分割
                        match_part = re.split(r'/', match)
                        # 列表中第一个字符添加到 last_logistics_codes 列表中
                        last_logistics_codes.append(match_part[0])
                    elif '-' in match:
                        # 转义’\/‘:re.split(r'-', match) 将字符串 match 按照 - 进行分割
                        match_part = re.split(r'-', match)
                        # 列表中第一个字符添加到 last_logistics_codes 列表中
                        last_logistics_codes.append(match_part[0])
                    elif '一件代发' in match:
                        dropshipping_logistics_codes = match
                    else:
                        dropshipping_logistics_codes = ''
        # 只取第二个字符串
        try:
            # AUASIAN: IN20240816094210+一件代发  最后一个<br\>为偏远
            last_result = last_logistics_codes[0] \
                if dropshipping_logistics_codes == '' or dropshipping_logistics_codes == '偏远' \
                else dropshipping_logistics_codes
            return last_result
        except IndexError:
            return 'None'

    # 正则搜索固定字符串
    @staticmethod
    def extract_print_str(html):
        """
        从给定的字典项中提取打印状态（已打印或未打印）。
        参数:
        html
        返回:
        str: '已打印' 或 '未打印' 如果找到匹配，否则返回 '未知状态'。
        """
        # 定义正则表达式模式
        pattern = r'已打印|未打印'

        # 进行正则表达式搜索
        match = re.search(pattern, html)

        # 检查匹配结果并返回相应的值
        if match:
            return match.group(0)
        else:
            return '未知状态'

    # 正则提取替换字符串：匹配 <br\/> 或 <br/> 标签并替换为空格
    @staticmethod
    def extract_replace_str(html):
        """
        从给定的字符串中提取字符串，去掉 HTML 换行标签。
        参数:
        item (str): 需要提取替换的字符串。
        返回:
        str: 提取并格式化后的字符。
        <br 匹配 <br。
        \s* 匹配零个或多个空白字符（包括空格、制表符等）。
        \/? 匹配零个或一个 /。
        > 匹配 >。
        """
        # 定义正则表达式模式，匹配 <br\/> 或 <br/> 标签
        pattern = r'<br\s*\/?>'

        # 使用 re.sub 替换掉匹配的 HTML 换行标签
        cleaned_text = re.sub(pattern, ' ', html)

        return cleaned_text

    # 提取html中相关信息,兼容两种html格式,并格式化字符.
    @staticmethod
    def extract_html_info(html):
        """
        从给定的 HTML 字符串中提取物流信息。

        参数:
        html (str): 包含需要信息的 HTML 字符串。

        返回:
        str: 提取并格式化后的HTML信息字符串。
        """
        # 定义正则表达式模式：
        # 匹配物流公司名称：(.*?)：捕获从字符串开始到 <br/> 标签之间的所有字符。
        carrier_pattern = r'^(.*?)<br\/>'
        # 匹配追踪号码：(.*?)：捕获 <a> 标签中的内容。
        tracking_number_pattern = r'<a[^>]*?class="outer_carrier_tracking_number"[^>]*?>(.*?)<\/a>'
        # 匹配URL：([^"]*?)：捕获 href 属性中的 URL。
        url_pattern = r'<a[^>]*?href="([^"]*?)"[^>]*?>'

        # 提取物流公司名称：strip()去除前后的空白字符
        carrier_match = re.search(carrier_pattern, html)
        carrier = carrier_match.group(1).strip() if carrier_match else ""

        # 提取追踪号码
        tracking_number_match = re.search(tracking_number_pattern, html)
        tracking_number = tracking_number_match.group(1).strip() if tracking_number_match else ""
        if "卡派" in html:
            courier_number = ''
        else:
            courier_number = tracking_number

        # 提取URL
        url_match = re.search(url_pattern, html)
        url = url_match.group(1).strip() if url_match else ""

        # 如果没有找到追踪号码和URL，检查是否有简单的格式
        if not tracking_number and not url:
            # 尝试匹配简单格式
            simple_pattern = r'<br\/>(.*)$'
            simple_match = re.search(simple_pattern, html)
            tracking_number = simple_match.group(1).strip() if simple_match else ""

        # 格式化结果
        result = f"{carrier} {tracking_number} {url}".strip()
        # 返回元组格式("result","courier_number")
        return result, courier_number

    # 匹配一个 <font> 标签及其内容，并捕获标签内的文本内容
    @staticmethod
    def extract_html_font(html):
        """
        :param html:
        :return: string
        (.*?):
        () 是捕获组，用于捕获匹配的内容。
        . 表示匹配除换行符之外的任何单个字符。
        * 是量词，表示前面的字符可以出现零次或多次。
        ? 是非贪婪量词，表示匹配尽可能少的字符。
        组合起来，(.*?) 表示匹配尽可能少的任意字符，并将其捕获。
        """
        # 将输入转换为字符串:要在整数中查找字符是不合理的，整数类型的对象不能被迭代
        html = str(html)
        # 定义正则表达式模式，匹配 <font> 标签及其内容:\s 匹配任意空白字符，包括空格、制表符和换行符。
        # * 是量词，表示匹配前面的元素 0 次或多次。\s* 匹配 0 个或多个空白字符。这个部分允许 <br> 标签和可能存在的空白字符之间的容忍度。
        pattern = r'<fon\s*t[^>]*>(.*?)</font>'

        # 检查是否包含 HTML 标签
        if '<' in html and '>' in html:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        else:
            # 如果没有 HTML 标签，直接返回输入内容
            return html

    # 匹配一个 <sapn> 标签及其内容，并捕获标签内的文本内容
    @staticmethod
    def extract_html_sapn(html):
        """
        :param html:
        :return: string
        """
        # 将输入转换为字符串:要在整数中查找字符是不合理的，整数类型的对象不能被迭代
        html = str(html)
        # 定义正则表达式模式，匹配 <font> 标签及其内容
        pattern = r'<sapn[^>]*>(.*?)</sapn>'
        # 检查是否包含 HTML 标签
        if '<' in html and '>' in html:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        else:
            # 如果没有 HTML 标签，直接返回输入内容
            return html

    @staticmethod
    def extract_first_tracking_number(shipment_id):
        """
        提取第一个跟踪号码。
        :param shipment_id: 包含单号的字符串，可能包含 '/', '//'，'-' 和空格作为分隔符
        :return: 第一个跟踪号码
        """
        # 使用正则表达式匹配 '/', '//' ,'-'和空格，并分割字符串
        if shipment_id is not None:
            split_numbers = re.split(r'[ /-]+', shipment_id)
        else:
            # 处理 None 的情况，例如赋予默认值或抛出一个更详细的错误
            split_numbers = []

        # 如果分割后的列表不为空，返回第一个元素，否则返回空字符串
        return split_numbers[0] if split_numbers else 'None'


# 先实例化类然后通过实例来调用方法:时间戳
class TimestampConverter:
    """
        转化时间戳：
        timestamp = 1722396365
        converter = TimestampConverter(timestamp)
        readable_time = converter.to_readable_string()
        iso8601_time = converter.to_iso8601_string()
        print(readable_time)  # 输出示例：2024-08-30 23:06:05
        print(iso8601_time)  # 输出示例：2024-08-30T23:06:05
            """

    # 类定义 (class) 和类构造函数 (__init__),封装数据和功能的工具
    # __init__(self, timestamp) 是类的构造函数。当我们创建类的实例时，这个构造函数会被调用，用来初始化对象。self 表示类的实例，timestamp 是我们传入的时间戳
    # self.timestamp = timestamp 将传入的时间戳存储在实例变量 self.timestamp 中，这样以后可以在类的方法中访问它。
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def to_readable_string(self):
        # 将时间戳转换为 datetime 对象
        dt_object = datetime.fromtimestamp(self.timestamp)
        # 格式化为可读字符串
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time

    def to_iso8601_string(self):
        # 将时间戳转换为 datetime 对象
        dt_object = datetime.fromtimestamp(self.timestamp)
        # 格式化为 ISO 8601 格式字符串
        iso_formatted_time = dt_object.isoformat()
        return iso_formatted_time


# 上下文管理器和 with 语句
class DatabaseConnector:
    """
        1.__enter__ 方法:
            当 with 语句开始执行时调用 __enter__ 方法。
            它通常负责资源的初始化。在这里，我们调用 connect 方法来建立数据库连接。
            __enter__ 方法返回的值会赋给 db_connector 对象，这使得你可以在 with 块中访问 self.connection。
        2.__exit__ 方法:
            当 with 语句块结束时，不管是正常结束还是由于异常结束，都会调用 __exit__ 方法。
            它用于清理资源。在这里，我们调用 disconnect 方法来关闭数据库连接。
            __exit__ 方法接收三个参数：异常类型 (exc_type)，异常值 (exc_val) 和追踪信息 (exc_tb)。
            如果没有异常，这些参数都是 None。如果发生了异常，你可以选择在这里处理它们。
            返回 False 意味着如果有异常发生，它会继续传播。如果返回 True，异常会被压制。
            """

    def __init__(self, ):
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        self.host = config['Database']['host']
        self.port = int(config['Database']['port'])
        self.user = config['Database']['user']
        self.password = config['Database']['password']
        self.database = config['Database']['database']
        self.connection = None

    # 连接数据库的实例方法
    def connect_to_database(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            # print("连接成功")
            return self.connection
        except MySQLError as e:
            logger.info(f"连接失败: {e}")
            return None

    # 如果存在数据库连接则断开，否则提示没有连接要断开
    def disconnect(self):
        if self.connection:
            self.connection.close()
            # print("断开连接成功")
        else:
            logger.info("没有连接需要断开")

    def __enter__(self):
        self.connect_to_database()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 在退出上下文管理器时确保事务一致性
        if self.connection:
            try:
                if exc_type:
                    logger.info("发生异常, 回滚事务")
                    self.connection.rollback()
                else:
                    # print("没有异常, 提交事务")
                    self.connection.commit()
            except MySQLError as e:
                logger.info(f"事务处理失败: {e}")

        self.disconnect()
        if exc_type:
            logger.info(f"异常类型: {exc_type}")
            logger.info(f"异常值: {exc_val}")
            logger.info(f"追踪信息: {exc_tb}")
        return True


class init_redis:

    def __redis__(self):
        """
        初始化连接redis
        :return:
        """
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        try:
            """
            在 redis-py 库中，decode_responses=True 参数的作用是将从 Redis 返回的字节数据自动解码为 Python 字符串。
            默认情况下，Redis 返回的数据是字节类型（bytes），如果设置了 decode_responses=True，则返回的数据会被解码为字符串（str）。
            self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
            从配置文件中读取redis连接信息，prot和db不是字符，需要转换
            StrictRedis 类：提供了对 Redis 数据库进行操作的方法和功能
            """
            self.redis_client = redis.StrictRedis(host=config['Redis']['host'], port=int(config['Redis']['port']),
                                                  password=config['Redis']['password'],
                                                  db=int(config['Redis']['db']), decode_responses=True)
            return self.redis_client
        except Exception as e:
            raise Exception(f"Failed to initialize Redis client: {e}")


# 处理时间戳：静态方法不需要实例化，即不需要创建类的实例，就可以直接通过类名来调用
class TimestampFormatter:
    @staticmethod
    def format_timestamp(unix_timestamp):
        try:
            dt = datetime.fromtimestamp(int(unix_timestamp))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"Error parsing timestamp: {e}")
            return unix_timestamp  # 如果解析失败，返回原始的时间戳

    @staticmethod
    def format_tostring(date_string):
        try:
            dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            return int(dt.timestamp())  # 转换为 Unix 时间戳
        except ValueError as e:
            print(f"Error parsing date string: {e}")
            return date_string  # 如果解析失败，返回原始的日期字符串


class BaseCrawlerView:
    def __init__(self, data_dict: dict):
        self.data_list = data_dict['data']['components']['gridView']['table']['dataSource']

    def get_viewid(self):
        view_list_id = []
        for data in self.data_list:
            # # 索引是从 0 开始的,返回 'lists' 最后一次出现的索引-->48,切片操作是左闭右开的,+1是为了取到本身'/'
            # index = self.data_url.rindex('/') + 1
            # # 从a的开始取到 index 位置的前一个字符;a[index:]-->那么切片将一直进行到 a 的结束。
            # part_url = self.data_url[:index]
            # view_url = f"{part_url}view?id={data['id']}"
            view_list_id.append(data['id'])
        return view_list_id

    @staticmethod
    def extract_view_year(status, year, date_pattern):
        date_re = re.search(date_pattern, status).group(0) if re.search(date_pattern, status) else None
        if date_re is not None:
            # 存在9.1   9/1 9-1 "." 替换为 "/"
            date = date_re.replace(".", "/").replace("-", "/")
            # 将日期字符串解析为datetime对象，假设年份为当前年份
            date_object = datetime.strptime(str(year) + '/' + date, '%Y/%m/%d')
            # 将datetime对象格式化为"年-月-日"格式
            return date_object.strftime('%Y-%m-%d')
        return None

    @staticmethod
    def extract_aaf_view_info(id: str, logistics_provider: str, text: str, status_list: list):
        """
        :param id:
        :param logistics_provider:
        :param text:
        :param status_list:
        :return:
        """
        id = id  # id
        logistics_provider = logistics_provider  # 物流商
        shipment_id_text = re.search(r"客户单号：</br>(.*?)</br>", text)  # 物流商单号
        sailing_date = None  # 开航日期
        customs_clearance_date = None  # 清关日期
        fetch_date = None  # 提取日期
        send_date = None  # 派送日期
        receipt_date = None  # 签收日期
        # 反向的迭代器
        list_reversed = status_list[::-1]
        result = []

        created = list_reversed[1] if list_reversed[1] else None  # 下单时间

        if "已离港" in list_reversed:
            sailing_index = list_reversed.index("已离港")  # 索引是从 0 开始的
            sailing_date = list_reversed[sailing_index + 1] if sailing_index > 0 else None

        for status in list_reversed:
            if "清关已放行" in status or "待上火车转" in status:
                customs_clearance_index = list_reversed.index(status)
                customs_clearance_date = list_reversed[
                    customs_clearance_index + 1] if customs_clearance_index > 0 else None
                # 清关日期是不是所有都-1天--？不用减了，按照最新的来
                # if customs_clearance_date:
                #     customs_clearance_date = (
                #                 datetime.strptime(customs_clearance_date, "%Y-%m-%d %H:%M:%S") - timedelta(days=1)).strftime(
                #         "%Y-%m-%d %H:%M:%S")
                break

        for status in list_reversed:
            if "已提柜" in status or "待上火车转" in status:
                status_index = list_reversed.index(status)
                fetch_date = list_reversed[status_index + 1] if status_index > 0 else None
                send_date = fetch_date
                break

        for status in status_list:
            if "已派送目的地" in status or "DELIVERED" in status:
                status_index = status_list.index(status)
                receipt_date = status_list[status_index - 1] if status_index > 0 else None
                if receipt_date is not None:
                    break

        shipment_id_str = shipment_id_text.group(1) if shipment_id_text else "None"
        shipment_id = RegularExpressionHtml.extract_first_tracking_number(shipment_id_str)
        result.append(
            (id, logistics_provider, shipment_id, created, sailing_date, customs_clearance_date, fetch_date, send_date,
             receipt_date))
        """
        外层解析：遍历原始数据列表中的每个元组record。
        内层解析：遍历每个元组中的每个元素item，如果该元素是None，则将其替换为字符串'None'，否则保持不变。
        """
        converted_str = [
            tuple('None' if item is None else item for item in record)
            for record in result
        ]
        return converted_str

    @staticmethod
    def extract_ges_view_info(id: str, logistics_provider: str, text: str, status_list: list):
        """
        :param id:
        :param logistics_provider:
        :param text:
        :param status_list:
        :return:
        """
        id = id  # id
        logistics_provider = logistics_provider  # 物流商
        shipment_id_text = re.search(r"客户单号：</br>(.*?)</br>", text)  # 物流商单号
        sailing_date = None  # 开航日期
        customs_clearance_date = None  # 清关日期
        fetch_date = None  # 提取日期
        send_date = None  # 派送日期
        receipt_date = None  # 签收日期
        # 反向的迭代器
        list_reversed = status_list[::-1]
        result = []
        created = list_reversed[1] if list_reversed[1] else None  # 下单时间
        # 会匹配到'第一个'出现的日期格式-->r'ETA(\d{1,2}/\d{1,2})' 会匹配 "ETA" 后面的日期,group(1) 则是第一个括号里面的内容;（group(0)）:"ETA8/11"
        # \d{1,2} 匹配 1 到 2 位的数字，[./] 匹配点或斜线，然后 \d{1,2} 再次匹配 1 到 2 位的数字。所以这个正则表达式可以匹配形如 "1/1"，"12/12"，"1.1"，"12.12" 的字符串。
        # compile() 函数用于将一个字符串编译为正则表达式模式对象
        date_pattern = re.compile(r'\d{1,2}[./-]\d{1,2}')
        status_keywords = ["已开船", "开船", "ETD", "International shipment release"]
        for status_keyword in status_keywords:
            for status in list_reversed:
                if status_keyword in status:
                    date_pattern_ymd = re.compile(r'\d{1,4}[./-]\d{1,2}[./-]\d{1,2}')
                    # 匹配年/月/日格式的日期，如果没有找到匹配项，那么 search() 会返回 None。
                    # year = str(int(year) + 1)  # 年份加1
                    match = re.search(date_pattern_ymd, status)
                    if match:
                        # logging.INFO(f"年/月/日格式的跨年日期: {id}")
                        date = match.group()
                        date_object = date.replace(".", "-").replace("/", "-")
                        sailing_date = date_object
                        break
                    status_index = list_reversed.index(status)
                    status_date = list_reversed[status_index + 1] if status_index > 0 else None
                    # 将这个字符串解析为一个datetime对象
                    datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                    # 从这个对象中获取年份
                    year = datetime_object.year
                    sailing_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                    if sailing_date is not None:
                        break
                    else:
                        sailing_date = list_reversed[status_index + 1] if status_index > 0 else None
                        break
            if sailing_date is not None:
                break

        for status in list_reversed:
            if any(keyword in status for keyword in
                   ["清关放行", "清关", "International shipment release - Import[MEMPHIS, TN, US]", "提柜", "已到港，待卸船"
                       , "已到港", "Arrived at Facility"]):
                status_index = list_reversed.index(status)
                customs_clearance_date = list_reversed[status_index + 1] if status_index > 0 else None
                break
            elif "到港" in status:
                date_pattern_ymd = re.compile(r'\d{1,4}[./-]\d{1,2}[./-]\d{1,2}')
                # 匹配年/月/日格式的日期，如果没有找到匹配项，那么 search() 会返回 None。
                # year = str(int(year) + 1)  # 年份加1
                match = re.search(date_pattern_ymd, status)
                if match:
                    # logging.INFO(f"年/月/日格式的跨年日期: {id}")
                    date = match.group()
                    date_object = date.replace(".", "-").replace("/", "-")
                    customs_clearance_date = date_object
                    break
                matches = date_pattern.findall(status)
                # 最后一个匹配的日期,如果字符串中没有与正则表达式匹配的部分，那么 findall() 会返回一个空列表。
                if matches:
                    last_date = matches[-1]
                    status_index = list_reversed.index(status)
                    status_date = list_reversed[status_index + 1] if status_index > 0 else None
                    # 将这个字符串解析为一个datetime对象
                    datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                    # 从这个对象中获取年份
                    year = datetime_object.year
                    # 存在9.1   9/1 9-1 "." 替换为 "/"
                    date = last_date.replace(".", "/").replace("-", "/")
                    # 将日期字符串解析为datetime对象，假设年份为当前年份
                    date_object = datetime.strptime(str(year) + '/' + date, '%Y/%m/%d')
                    # 将datetime对象格式化为"年-月-日"格式
                    customs_clearance_date = date_object.strftime('%Y-%m-%d')
                    break
                else:
                    customs_clearance_date = None

        for status in list_reversed:
            if any(keyword in status for keyword in
                   ["柜子已提出", "Arrived at Facility", "Departed FedEx hub[MEMPHIS, TN, US]"]):
                status_index = list_reversed.index(status)
                fetch_date = list_reversed[status_index + 1] if status_index > 0 else None
                break
            elif "交仓" in status or "送仓" in status:
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index + 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                fetch_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if fetch_date is not None:
                    break

        status_keywords = ["Arrived at Facility", "Departed from Facility"]
        for status_keyword in status_keywords:
            for status in list_reversed:
                if "预约美国" in status or "送仓" in status or "递送" in status or "交仓" in status or "派送" in status:
                    date_pattern_ymd = re.compile(r'\d{1,4}[./-]\d{1,2}[./-]\d{1,2}')
                    # 匹配年/月/日格式的日期，如果没有找到匹配项，那么 search() 会返回 None。
                    # year = str(int(year) + 1)  # 年份加1
                    match = re.search(date_pattern_ymd, status)
                    if match:
                        # logging.INFO(f"年/月/日格式的跨年日期: {id}")
                        date = match.group()
                        date_object = date.replace(".", "-").replace("/", "-")
                        send_date = date_object
                        break
                    matches = date_pattern.findall(status)
                    # 最后一个匹配的日期,如果字符串中没有与正则表达式匹配的部分，那么 findall() 会返回一个空列表。
                    if matches:
                        last_date = matches[-1]
                        status_index = list_reversed.index(status)
                        status_date = list_reversed[status_index + 1] if status_index > 0 else None
                        # 将这个字符串解析为一个datetime对象
                        datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                        # 从这个对象中获取年份
                        year = datetime_object.year
                        # 存在9.1   9/1 9-1 "." 替换为 "/"
                        date = last_date.replace(".", "/").replace("-", "/")
                        # 将日期字符串解析为datetime对象，假设年份为当前年份
                        date_object = datetime.strptime(str(year) + '/' + date, '%Y/%m/%d')
                        # 将datetime对象格式化为"年-月-日"格式
                        send_date = date_object.strftime('%Y-%m-%d')
                        break
                    else:
                        send_date = None
                elif status_keyword in status:
                    status_index = list_reversed.index(status)
                    send_date = list_reversed[status_index + 1] if status_index > 0 else None
                    break
            if send_date is not None:
                break


        for status in status_list:
            if "签收" in status or "已递送" in status or "已送仓" in status or "已交仓" in status:
                status_index = status_list.index(status)
                status_date = status_list[status_index - 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                receipt_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if receipt_date is not None:
                    break
                else:
                    receipt_date = status_list[status_index - 1] if status_index > 0 else None
                    break
            elif "DELIVERED" in status:
                status_index = status_list.index(status)
                receipt_date = status_list[status_index - 1] if status_index > 0 else None
                break
            elif "附件" in status:
                status_index = status_list.index(status)
                receipt_date = status_list[status_index - 1] if status_index > 0 else None
                break

        if send_date is None and receipt_date is not None:
            send_date = receipt_date

        shipment_id_str = shipment_id_text.group(1) if shipment_id_text else "None"
        shipment_id = RegularExpressionHtml.extract_first_tracking_number(shipment_id_str)
        result.append(
            (id, logistics_provider, shipment_id, created, sailing_date, customs_clearance_date, fetch_date, send_date,
             receipt_date))
        converted_str = [
            tuple('None' if item is None else item for item in record)
            for record in result
        ]
        return converted_str

    @staticmethod
    def extract_auasian_view_info(id: str, logistics_provider: str, text: str, status_list: list):
        """
        :param id:
        :param logistics_provider:
        :param text:
        :param status_list:
        :return:
        """
        id = id  # id
        logistics_provider = logistics_provider  # 物流商
        shipment_id_text = re.search(r"客户单号：</br>(.*?)</br>", text)  # 物流商单号
        sailing_date = None  # 开航日期
        customs_clearance_date = None  # 清关日期
        fetch_date = None  # 提取日期
        send_date = None  # 派送日期
        receipt_date = None  # 签收日期
        # 反向的迭代器
        list_reversed = status_list[::-1]
        result = []
        created = list_reversed[1] if list_reversed[1] else None  # 下单时间
        # 会匹配到第一个出现的日期格式-->r'ETA(\d{1,2}/\d{1,2})' 会匹配 "ETA" 后面的日期,group(1) 则是第一个括号里面的内容,（group(0)）:"ETA8/11"
        date_pattern = re.compile(r'\d{1,2}[./-]\d{1,2}')

        for status in list_reversed:
            # \s+ 来匹配一个或多个空格
            pattern = "(厦门码头\s+发往\s+洛杉)|(上海码头\s+发往\s+洛杉)|(宁波码头\s+发往\s+洛杉)"
            status_re = re.search(pattern, status)
            if status_re is not None:
                status_index = list_reversed.index(status)
                sailing_date = list_reversed[status_index + 1] if status_index > 0 else None
                break

        for status in list_reversed:
            pattern_A = "美国时间\d+[\./-]\d+到洛杉矶"
            pattern_B = "美国时间\d+[\./-]\d+到港"
            if re.search(pattern_A, status) or re.search(pattern_B, status):
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index + 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                customs_clearance_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if customs_clearance_date is not None:
                    break

        for status in list_reversed:
            pattern_A = "美国时间\d+[\./-]\d+柜子提回"
            pattern_B = "美国时间\d+[\./-]\d+\s*已签收"
            # 将会检查 status 是否包含列表中的任何一个子字符串。如果 status 包含列表中的任何一个子字符串，any 函数将返回 True。
            if re.search(pattern_A, status) or re.search(pattern_B, status):
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index + 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                fetch_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if fetch_date is not None:
                    break
            # any() 函数和列表推导式。any() 函数接受一个 iterable（如列表、元组等），如果 iterable 中的任何元素为真，它就返回 True,
            elif any(keyword in status for keyword in
                     ["Package is in transit to a UPS facility",
                      "Processing at UPS Facility", "Arrived at Facility"]):
                status_index = list_reversed.index(status)
                fetch_date = list_reversed[status_index + 1] if status_index > 0 else None
                break

        status_keywords = ["Arrived at Facility", "Departed from Facility"]
        for status_keyword in status_keywords:
            for status in list_reversed:
                # "?" 表示前面的字符可以出现0次或1次
                pattern_A = "\d+[\./-]\d+A?\s*卡派完成，POD已上传"
                pattern_B = "美国时间\d+[\./-]\d+\s*已签收"
                if status_keyword in status:
                    status_index = list_reversed.index(status)
                    send_date = list_reversed[status_index + 1] if status_index > 0 else None
                    break
                elif re.search(pattern_A, status) or re.search(pattern_B, status):
                    status_index = list_reversed.index(status)
                    status_date = list_reversed[status_index + 1] if status_index > 0 else None
                    # 将这个字符串解析为一个datetime对象
                    datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                    # 从这个对象中获取年份
                    year = datetime_object.year
                    send_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                    if send_date is not None:
                        break
            if send_date is not None:
                break

        for status in status_list:
            pattern_A = "\d+[\./-]\d+A?\s*卡派完成，POD已上传"
            pattern_B = "美国时间\d+[\./-]\d+\s*已签收"
            if re.search(pattern_A, status) or re.search(pattern_B, status):
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index - 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                receipt_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if receipt_date is not None:
                    break
            elif "DELIVERED" in status or "Delivered" in status:
                status_index = status_list.index(status)
                receipt_date = status_list[status_index - 1] if status_index > 0 else None
                break

        shipment_id_str = shipment_id_text.group(1) if shipment_id_text else None
        shipment_id = RegularExpressionHtml.extract_first_tracking_number(shipment_id_str)
        result.append(
            (id, logistics_provider, shipment_id, created, sailing_date, customs_clearance_date, fetch_date, send_date,
             receipt_date))
        converted_str = [
            tuple('None' if item is None else item for item in record)
            for record in result
        ]
        return converted_str


def get_ordered_dict(field_list: list, data_json: dict):
    """
    根据传入的过滤条件字段列表，补齐列表中没有的字段，构建一个有序的字典
    :param data_json: 需要插入到数据库的字典数据-->{"age": "Alice", "name": 25, "city": "New York"}
    :param field_list: 过滤条件字段-->["name", "age", "id", "city"]
    :return: ordered_dict： dict-->OrderedDict([('name', 25), ('age', 'Alice'), ('id', 'None'), ('city', 'New York')])
    type :<class 'collections.OrderedDict'>
    中间data_json： dict-->{'age': 'Alice', 'name': 25, 'city': 'New York', 'id': 'None'}
    """
    # 使用列表推导式创建一个新的列表 valid_field_order，这个列表只包含 field_list 中存在于 data_json 的字段
    # 这个步骤是为了确保我们只处理 data_json 中实际存在的字段
    # valid_field_order-->['name', 'age', 'city']
    valid_field_order = [field for field in field_list if field in data_json]
    # set_A -->{'name', 'city', 'age'}
    set_A = set(valid_field_order)
    # set_B -->{'name', 'id', 'city', 'age'}
    set_B = set(field_list)
    # 查找两个列表中不相同的字段 results-->{'id'}  type--><class 'set'>
    results = set_A.symmetric_difference(set_B)
    if results:
        for result in results:
            data_json[result] = "None"
    ordered_dict = OrderedDict([(field, data_json[field]) for field in field_list])
    return ordered_dict


def create_ordered_dict(field_list: list, unordered_dict: dict):
    """
    根据传入的列表字段参数，构建一个有序的字典
    :param unordered_dict: 需要插入到数据库的字典数据:{"name": "Alice", "age": 25, "city": "New York"}
    :param field_list: 数据库字段:["name", "age", "city"]
    :return: 特殊字典类型的实例:OrderedDict([('name', 'Alice'), ('age', 25), ('city', 'New York')])
    OrderedDict 是 Python 的 collections 模块中的一个类，它提供了一个在迭代时保持元素插入顺序的字典。
    与普通的字典不同，OrderedDict 会记住插入键值对的顺序。在你的例子中，如果你遍历这个 OrderedDict，
    你会得到 'name', 'age', 'city' 这个顺序的键，而不是在普通字典中可能得到的任意顺序的键。
    """

    # 使用列表推导式创建一个新的列表 valid_field_order，这个列表只包含 field_list 中存在于 unordered_dict 的字段
    # 这个步骤是为了确保我们只处理 unordered_dict 中实际存在的字段
    valid_field_order = [field for field in field_list if field in unordered_dict]

    len_valid_field_order = len(valid_field_order)
    len_field_list = len(field_list)
    """
    检查 valid_field_order 的长度是否等于 field_list 的长度.如果不等，说明 unordered_dict 中没有 field_list 的某些字段,
    这可能是一个错误.在这种情况下，函数会记录一个错误消息,并返回 None
    """
    if len_valid_field_order != len_field_list:
        logger.error(f"field_list:{field_list} , unordered_dict:{unordered_dict} 数据库字段个数与数据字典的个数不一致！")
        return None
    """
    使用列表推导式和 OrderedDict 类创建一个有序的字典 ordered_dict.OrderedDict 是一个字典子类,它记住了元素插入的顺序.
    列表推导式创建了一个元素是元组的列表,每个元组的第一个元素是字段名,第二个元素是 unordered_dict 中对应字段的值.
    这个列表的顺序由 field_list 决定
    """
    ordered_dict = OrderedDict([(field, unordered_dict[field]) for field in field_list])
    return ordered_dict


def get_dict_value(json_data: dict):
    """
    获取字典的values，转化为字符转类型
    :param json_data: 插入数据库的数据:OrderedDict([('name', 'Alice'), ('age', 25), ('city', 'New York')])
    或者 {'age': 'Alice', 'name': 25, 'city': 'New York', 'id': 'None'}-->json_data.values()取出来的都是单个键的值。
    :return: 返回 元组类型 的 字符串:"('Alice', '25', 'New York')"
    """
    value_list = []
    # 如果是字符串类型的value，则直接不做处理，如果是非字符串类型的value，则进行解码
    for value in json_data.values():
        # isinstance 函数检查每个值是否为字符串类型
        if isinstance(value, str):
            str_value = value
        else:
            # 转换为 JSON 格式的字符串 25-->'25'
            str_value = json.dumps(value)
        value_list.append(str_value)
    # 使用 tuple 函数将 value_list:['Alice', '25', 'New York'] 转换为元组:('Alice', '25', 'New York')
    tup_data = tuple(value_list)
    # 使用 str 函数将 tup_data 转换为字符串:"('Alice', '25', 'New York')"
    sql_data = str(tup_data)
    return sql_data


def list_to_sql_values(field_list: list, data_list: [dict]):
    """
    将列表套字典格式的数据，转化为字符串类型的元组：(...),(...),(...)
    :param field_list: 字段列表:["name", "age", "city"]
    :param data_list: 插入数据库的数据列表:data_list = [
    {"name": "Alice", "age": 25, "city": "New York"},
    {"name": "Bob", "age": 30, "city": "Los Angeles"},]
    :return: 字符串类型的元组:"('Alice', '25', 'New York'),('Bob', '30', 'Los Angeles')"
    db_table = "test_table"
    field_list = ["name", "age", "city"]
    data_list = [
    {"name": "Alice", "age": 25, "city": "New York"},
    {"name": "Bob", "age": 30, "city": "Los Angeles"},]
    """
    # 循环之后的结果：["('Alice', '25', 'New York')","('Bob', '30', 'Los Angeles')"]
    value_list = []
    for json_data in data_list:
        # 根据传入的过滤条件字段列表，补齐列表中没有的字段，构建一个有序的字典
        ordered_dict = get_ordered_dict(field_list, json_data)
        # 获取字典的values，转化为字符转类型
        sql_data = get_dict_value(ordered_dict)
        value_list.append(sql_data)
    # 将 列表中的所有字符串连接成一个字符串,每个字符串之间用逗号分隔.
    # "('Alice', '25', 'New York'), ('Bob', '30', 'Los Angeles')"
    sql_values = ",".join(value_list)
    return sql_values


def create_insert_sql(db_table: str, field_list: list, sql_values: str):
    """
    根据字段列表 和 字段对应需要插入的数据，构建出insert的sql语句
    :param db_table: 数据库表名称:test_table
    :param field_list: 字段列表:["name", "age", "city"]
    :param sql_values: 字段对应需要插入的values:"('Alice', '25', 'New York'),('Bob', '30', 'Los Angeles')"
    :return: str:
    """

    # 使用 ', '.join() 将列表组合成完整的结果字符串:'name, age, city'
    result_str = ', '.join(field_list)
    # 使用一个生成器表达式创建了一个新的列表 value_strs:['name=values(name)', 'age=values(age)', 'city=values(city)']
    value_strs = [f"{field}=values({field})" for field in field_list]
    """
    拼接sql："
    INSERT INTO test_table(name, age, city) 
    VALUES ('Alice', '25', 'New York'),('Bob', '30', 'Los Angeles') 
    ON DUPLICATE KEY UPDATE 
    name=values(name), age=values(age), city=values(city)"
    """
    insert_sql = f"INSERT INTO {db_table}({result_str}) VALUES {sql_values} ON DUPLICATE KEY UPDATE {', '.join(value_strs)}"
    return insert_sql
