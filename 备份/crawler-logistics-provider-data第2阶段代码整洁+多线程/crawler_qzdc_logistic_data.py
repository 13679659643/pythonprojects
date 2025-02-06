# -*- coding: utf-8 -*-
# @Time    : 2024/9/6 16:42
# @Author  : Night
# @File    : crawler_qzdc_logistic_data.py
# @Description: 中通物流采集
import copy
import queue
import re
from datetime import datetime
from loguru import logger
from crawler_base import BaseCrawler
from lxml import html
import requests
from db_model import ods_scg_wld_logistics_zto_table, ods_scg_wld_logistics_zto_i_d_field_list, \
    ods_scg_wld_logistics_zto_track_table, ods_scg_wld_logistics_zto_track_i_d_field_list
from method import RetryDecorator


class CrawlerZtLogisticData(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.session = requests.session()
        self.zto_queue = queue.Queue()

    @RetryDecorator.retry(max_attempts=3)
    def get_login_cookie(self):
        """
        中通 自动化登录 时效一般2小时内
        :return:
        """
        with self.redis_client.conn as redis_conn:
            if not redis_conn.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                data = {
                    'usertype': 'client',
                    'userid': self.config[self.logistics_provider_code]['username'],
                    'password': self.config[self.logistics_provider_code]['password'],
                    'logontype': 'userAccount',
                    'pcinfo': '{"os":"windows"}',
                }
                response = self.session.post(self.token_url,
                                             data=data, verify=False)
                if response.status_code == 200:
                    session_id = response.headers['Set-Cookie']
                    redis_conn.hset(self.HASH_AUTH_TOKEN, self.key, session_id)
                    redis_conn.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 2 * 60 * 60, "1")
                    logger.info("中通-登录账号成功")
                else:
                    logger.warning(f"登录请求失败，状态码：{response.status_code}")
                    return None
            return redis_conn.hget(self.HASH_AUTH_TOKEN, self.key)

    def init_headers(self, session_cookie):
        self.session.headers['cookie'] = session_cookie.decode()

    def normalize_tracking_numbers(self, tracking_numbers):
        """
        将包含多种分隔符的单号字符串转换为逗号分隔的格式。
        :param tracking_numbers: 包含单号的字符串，可能包含 '/', '//' 和空格作为分隔符
        :return: 逗号分隔的单号字符串
        """
        # 使用正则表达式匹配 '/', '//' 和空格，并替换为逗号
        normalized_numbers = re.sub(r'[ /]+', ',', tracking_numbers)
        return normalized_numbers.strip()

    def get_order_management(self):
        """
        获取 订单管理 全部数据
        :return:
        """
        page = 1
        limit = 200
        while True:
            data = {
                'page': page,
                'limit': limit,
                'search.border.status': '',
            }
            response = self.session.post(self.data_url, data=data, verify=False)
            if response.status_code != 200:
                return {}
            data = response.json()
            data_list = data.get("data", [])
            if not data_list:
                return
            new_data = []
            for row in data_list:
                row_copy = copy.deepcopy(row)
                row_copy['dt'] = row_copy['receiptdate'].split(" ")[0].replace("-", "")
                fba_number_str = self.normalize_tracking_numbers(row_copy['fbanumber'])
                fba_numbers = [] if fba_number_str == "" else fba_number_str.split(",")
                for fba_number in fba_numbers:
                    new_row = copy.deepcopy(row_copy)
                    new_row['fbanumber'] = fba_number
                    new_data.append(new_row)
                self.zto_queue.put(row['pkid'])
            self.tidb.insert_data(ods_scg_wld_logistics_zto_table, ods_scg_wld_logistics_zto_i_d_field_list,
                                  new_data)
            logger.info(f"中通-物流信息数据同步{len(new_data)}完成")
            total_count = data['count']
            total_page = (total_count + limit - 1) / limit
            if page >= total_page:
                break
            page += 1

    def extract_date_from_description(self, track_data: dict):
        """
        从 track_des 中提取日期，如果无法提取则使用 track_date。
        :param track_data: 包含 'track_date' 和 'track_des' 的字典
        :return: 补全年份后的日期字符串，格式为 YYYY-MM-DD
        """
        track_date_str = track_data.get('track_date', '')
        track_des = track_data.get('track_des', '')

        # 尝试从 track_des 中提取完整日期，格式为 YYYY-MM-DD
        full_date_match = re.search(r'(\d{4}-\d{2}-\d{2})', track_des)
        if full_date_match:
            full_date_str = full_date_match.group(1)
            return full_date_str

        # 尝试从 track_des 中提取日期
        date_match = re.search(r'(\d{1,2}[./]\d{1,2})', track_des)
        if date_match:
            date_part = date_match.group(1)
            month, day = map(int, re.split(r'[./]', date_part))
            track_date = datetime.strptime(track_date_str, '%Y-%m-%d %H:%M:%S')
            year = track_date.year
            full_date = datetime(year, month, day)
            return full_date.strftime('%Y-%m-%d')
        else:
            # 如果无法从 track_des 中提取日期，直接使用 track_date
            return track_date_str.split(' ')[0]

    def etl_track_data(self, row_data: list):
        """
        路由轨迹数据处理
        :return:
        """
        track_dict = {
            'departure_date': '',  # 开航日期
            'clearance_date': '',  # 清关日期
            'extraction_date': '',  # 提取日期
            'delivery_date': '',  # 派送日期
            'signing_date': '',  # 签收日期
        }
        sail_count = 0
        for index, row in enumerate(row_data):
            track = row['track_des']
            if '已开船' in track or '已发车' in track:
                sail_count += 1
                if sail_count == 1:
                    track_dict['departure_date'] = self.extract_date_from_description(row)
            elif '清关' in track:
                track_dict['clearance_date'] = self.extract_date_from_description(row)
            elif '已签收' in track or '已回传' in track:
                track_dict['signing_date'] = self.extract_date_from_description(row)

        return track_dict

    def get_logistic_track(self):
        """
        获取物流轨迹
        :return:
        """
        all_track_list = []
        while not self.zto_queue.empty():
            pk_id = self.zto_queue.get()
            params = {
                "pkid": str(pk_id)
            }
            track_url = 'http://112.74.95.234:9999/admin/waybill/order/orderTrack'
            response = self.session.get(track_url, params=params, verify=False)
            html_tree = response.text
            tree = html.fromstring(html_tree)
            ul = tree.xpath("//div[@id='orderTracks']//ul/li")
            track_list = []
            for li in ul[::-1]:
                item = {}
                track_date = li.xpath(".//span[@class='trackdate']/text()")[0]
                track_des = li.xpath(".//p[@class='info']/following-sibling::p[1]/text()")[0]
                item['track_date'] = track_date.strip()
                item['track_des'] = track_des.strip()
                track_list.append(item)

            track_dict = self.etl_track_data(track_list)
            track_dict['pkid'] = pk_id
            all_track_list.append(track_dict)

        self.tidb.insert_data(ods_scg_wld_logistics_zto_track_table, ods_scg_wld_logistics_zto_track_i_d_field_list,
                              all_track_list)
        logger.info(f"中通-路由轨迹数据同步{len(all_track_list)}完成")

    def main(self):
        self.init_logistic('ZTO')
        session_cookie = self.get_login_cookie()
        if not session_cookie:
            return
        self.init_headers(session_cookie)
        self.get_order_management()
        self.get_logistic_track()


if __name__ == "__main__":
    zt = CrawlerZtLogisticData()
    zt.main()
