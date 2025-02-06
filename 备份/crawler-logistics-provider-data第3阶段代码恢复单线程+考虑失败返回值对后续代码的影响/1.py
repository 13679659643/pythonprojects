import json
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
        shipment_id = re.search(r"客户单号：</br>(.*?)</br>", text)  # 物流商单号
        sailing_date = None  # 开航日期
        customs_clearance_date = None  # 清关日期
        fetch_date = None  # 提取日期
        send_date = None  # 派送日期
        receipt_date = None  # 签收日期
        # 反向的迭代器
        list_reversed = status_list[::-1]
        result = []

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

        shipment_id = shipment_id.group(1) if shipment_id else "None"
        result.append((id, logistics_provider, shipment_id, sailing_date, customs_clearance_date, fetch_date, send_date,
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
        shipment_id = re.search(r"客户单号：</br>(.*?)</br>", text)  # 物流商单号
        sailing_date = None  # 开航日期
        customs_clearance_date = None  # 清关日期
        fetch_date = None  # 提取日期
        send_date = None  # 派送日期
        receipt_date = None  # 签收日期
        # 反向的迭代器
        list_reversed = status_list[::-1]
        result = []
        # 会匹配到'第一个'出现的日期格式-->r'ETA(\d{1,2}/\d{1,2})' 会匹配 "ETA" 后面的日期,group(1) 则是第一个括号里面的内容;（group(0)）:"ETA8/11"
        # \d{1,2} 匹配 1 到 2 位的数字，[./] 匹配点或斜线，然后 \d{1,2} 再次匹配 1 到 2 位的数字。所以这个正则表达式可以匹配形如 "1/1"，"12/12"，"1.1"，"12.12" 的字符串。
        date_pattern = re.compile(r'\d{1,2}[./-]\d{1,2}')

        for status in list_reversed:
            if "ETD" in status:
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index + 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                sailing_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if sailing_date is not None:
                    break

        for status in list_reversed:
            if "已到港清关放行，待卸船" in status or "已清关放行" in status or "清关已放行" in status:
                status_index = list_reversed.index(status)
                customs_clearance_date = list_reversed[status_index + 1] if status_index > 0 else None
                break

        for status in list_reversed:
            if "柜子已提出" in status or "Arrived at Facility" in status:
                status_index = list_reversed.index(status)
                fetch_date = list_reversed[status_index + 1] if status_index > 0 else None
                break

        for status in list_reversed:
            if "预约美国" in status or "送仓" in status or "递送" in status:
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index + 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                send_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if send_date is not None:
                    break

        for status in status_list:
            if "签收" in status or "已递送" in status:
                status_index = status_list.index(status)
                status_date = status_list[status_index - 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                receipt_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if receipt_date is not None:
                    break
            elif "DELIVERED" in status:
                status_index = status_list.index(status)
                receipt_date = status_list[status_index - 1] if status_index > 0 else None
                break

        shipment_id = shipment_id.group(1) if shipment_id else None
        result.append((id, logistics_provider, shipment_id, sailing_date, customs_clearance_date, fetch_date, send_date,
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
        shipment_id = re.search(r"客户单号：</br>(.*?)</br>", text)  # 物流商单号
        sailing_date = None  # 开航日期
        customs_clearance_date = None  # 清关日期
        fetch_date = None  # 提取日期
        send_date = None  # 派送日期
        receipt_date = None  # 签收日期
        # 反向的迭代器
        list_reversed = status_list[::-1]
        result = []
        # 会匹配到第一个出现的日期格式-->r'ETA(\d{1,2}/\d{1,2})' 会匹配 "ETA" 后面的日期,group(1) 则是第一个括号里面的内容,（group(0)）:"ETA8/11"
        date_pattern = re.compile(r'\d{1,2}[./]\d{1,2}')

        for status in list_reversed:
            if "厦门码头 发往 洛杉机" in status or "上海码头 发往 洛杉矶" in status:
                status_index = list_reversed.index(status)
                sailing_date = list_reversed[status_index + 1] if status_index > 0 else None
                break

        for status in list_reversed:
            pattern_A = "美国时间\d+\.\d+到洛杉矶"
            pattern_B = "美国时间\d+\.\d+到港"
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
            pattern_A = "美国时间\d+\.\d+柜子提回"
            # 将会检查 status 是否包含列表中的任何一个子字符串。如果 status 包含列表中的任何一个子字符串，any 函数将返回 True。
            if re.search(pattern_A, status):
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index + 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                fetch_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if fetch_date is not None:
                    break
            elif any(keyword in status for keyword in
                     ["Package is in transit to a UPS facility", "Processing at UPS Facility",
                      "Departed from Facility[Hodgkins, IL, United States]"]):
                status_index = list_reversed.index(status)
                fetch_date = list_reversed[status_index + 1] if status_index > 0 else None
                break

        for status in list_reversed:
            pattern_A = "\d+\.\d+卡派完成，POD已上传"
            if any(keyword in status for keyword in
                   ["Arrived at Facility[Los Angeles, CA, United States]",
                    "Departed from Facility[Bayonne, NJ, United States]", "Arrived at Facility"]):
                status_index = list_reversed.index(status)
                send_date = list_reversed[status_index + 1] if status_index > 0 else None
                break
            elif re.search(pattern_A, status):
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index + 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                send_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if send_date is not None:
                    break

        for status in status_list:
            pattern_A = "\d+\.\d+卡派完成，POD已上传"
            if re.search(pattern_A, status):
                status_index = list_reversed.index(status)
                status_date = list_reversed[status_index - 1] if status_index > 0 else None
                # 将这个字符串解析为一个datetime对象
                datetime_object = datetime.strptime(status_date, '%Y-%m-%d %H:%M:%S')
                # 从这个对象中获取年份
                year = datetime_object.year
                receipt_date = BaseCrawlerView.extract_view_year(status, year, date_pattern)
                if receipt_date is not None:
                    break
            elif "DELIVERED" in status:
                status_index = list_reversed.index(status)
                sailing_date = list_reversed[status_index - 1] if status_index > 0 else None
                break

        shipment_id = shipment_id.group(1) if shipment_id else "None"
        result.append((id, logistics_provider, shipment_id, sailing_date, customs_clearance_date, fetch_date, send_date,
                       receipt_date))
        converted_str = [
            tuple('None' if item is None else item for item in record)
            for record in result
        ]
        return converted_str

a =["2022-08-07 15:30:59", "ETD : 3-7","2025-08-07 15:30:59"]
b = '22'
c = '33'
d = '客户单号：</br>11</br>'
print(BaseCrawlerView.extract_ges_view_info(b,c,d,a))