# -*- coding: utf-8 -*-
# @Time    : 2024/9/5 10:38
# @Author  : Night
# @File    : crawler_ahclog_logistic_data.py
# @Description: 快驿通物流采集
import queue
from crawler_base import BaseCrawler
import requests
import ddddocr
import base64
from io import BytesIO
from PIL import Image
from loguru import logger
import re
from db_model import ods_scg_wld_logistics_ahc_table, ods_scg_wld_logistics_ahc_i_d_field_list, \
    ods_scg_wld_logistics_ahc_cost_table, ods_scg_wld_logistics_ahc_cost_i_d_field_list, \
    ods_scg_wld_logistics_ahc_track_table, ods_scg_wld_logistics_ahc_track_i_d_field_list
from datetime import datetime, timedelta

from method import RetryDecorator


class CrawlerAhcLogisticData(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.session = requests.session()
        self.detail_ahc_queue = queue.Queue()
        self.now_date = datetime.now()
        self.end_date = datetime.now().strftime('%Y%m%d')
        self.start_date = (self.now_date - timedelta(days=90)).strftime('%Y%m%d')

    @RetryDecorator.retry(max_attempts=15)
    def identify_verification_code(self):
        """
        验证码识别
        通过ddddocr 识别 4+3=？ 这种算数验证码
        :return:
        """
        code_url = 'http://8.134.39.115:8000/cms/user/auth-code'
        response = self.session.get(code_url)
        if response.status_code == 200:
            jsonp_data = response.json()
            base64_data = jsonp_data['img'].split(',')[1]
            img_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(img_data))
            image.save('ach_code.png')
            uuid = jsonp_data['uuid']

            ocr = ddddocr.DdddOcr(beta=True, show_ad=False)
            with open("ach_code.png", "rb") as image_file:
                image = image_file.read()
            ocr.set_ranges("0123456789+-×÷=")
            img_expression = ocr.classification(image)
            pattern = r'(\d+)([\+\-\×\÷])(\d+)'
            match = re.match(pattern, img_expression)

            if not match:
                return None

            num1, operator, num2 = match.groups()
            num1 = int(num1)
            num2 = int(num2)

            # 根据运算符进行相应的计算
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '×':
                result = num1 * num2
            elif operator == '÷':
                result = num1 / num2
            else:
                return None
            return uuid, result
        return None

    @RetryDecorator.retry(max_attempts=15)
    def get_AccessToken(self):
        """
        获取登录标识 快驿通
        :return:
        """
        with self.redis_client.conn as redis_conn:
            if not redis_conn.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                uuid_and_code = self.identify_verification_code()
                if uuid_and_code:
                    uuid, code = uuid_and_code
                    json_data = {
                        'username': self.config[self.logistics_provider_code]['username'],
                        'password': self.config[self.logistics_provider_code]['password'],
                        'code': code,
                        'uuid': uuid,
                    }
                    acc_response = self.session.post(self.token_url, json=json_data, verify=False)
                    if acc_response.status_code == 200:
                        access_token = acc_response.json()['accessToken']
                        redis_conn.hset(self.HASH_AUTH_TOKEN, self.key, access_token)
                        redis_conn.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 2 * 60 * 60, "1")
                        logger.info("快驿通-登录账号成功")
                    else:
                        logger.warning(f"登录请求失败，状态码：{acc_response.status_code}")
                else:
                    logger.info("快驿通-获取验证码失败，重新获取验证码")

            return redis_conn.hget(self.HASH_AUTH_TOKEN, self.key)

    def init_headers(self, access_token):
        """
        初始化headers
        :param access_token:
        :return:
        """
        self.session.headers['authorization'] = 'Bearer ' + access_token.decode()

    def get_inbound_orders(self):
        """
        获取入库订单 状态 (全部)
        :return:
        """
        json_data = {
            'pagesize': 0,
            'pageno': 0,
            'reportno': 'ORDERMX',
            'opentype': 'find',
            'colen': 'find',
            'userquery1': self.start_date,
            'userquery2': self.end_date,
            'userquery4': 'allqty',
            'userquery3': '%',
        }
        response = self.session.post(self.data_url, json=json_data, verify=False)
        if response.status_code != 200:
            return {}
        data_list = response.json()
        if not data_list:
            return
        new_data = []
        for row in data_list:
            row['dt'] = row['sjdate'].replace("-", "")
            new_data.append(row)
            self.detail_ahc_queue.put(row['orderno'])

        self.tidb.insert_data(ods_scg_wld_logistics_ahc_table, ods_scg_wld_logistics_ahc_i_d_field_list, new_data)
        logger.info(f'快驿通-入仓订单数据同步{len(new_data)}完成')

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
        # FBA188WYGZ0G
        arrived_at_facility_count = 0
        clearances_count = 0
        reversed_data = row_data[::-1]
        for index, row in enumerate(reversed_data):
            track = row['guiji']
            if index == 0:
                track_dict['orderno'] = row['orderno']
                track_dict['packno'] = row['packno']
            if '已开航' in track or '已开船' in track or '预计开船' in track:
                track_dict['departure_date'] = row['zztm']
            elif '正在清关中' in track or '进口海关放行' in track:
                clearances_count += 1
                if clearances_count == 1:
                    track_dict['clearance_date'] = row['zztm']
            elif '已签收' in track:
                track_dict['signing_date'] = row['zztm']
                if arrived_at_facility_count == 0:
                    track_dict['extraction_date'] = row['zztm']
                    track_dict['delivery_date'] = row['zztm']
            elif 'Arrived at ' in track:
                arrived_at_facility_count += 1
                if arrived_at_facility_count == 1:
                    track_dict['extraction_date'] = row['zztm']
                    track_dict['delivery_date'] = row['zztm']
                elif arrived_at_facility_count == 2:
                    track_dict['delivery_date'] = row['zztm']
            elif '已签收' in track or 'Delivered' in track:
                track_dict['signing_date'] = row['zztm']
        return track_dict

    def get_detail_orders(self):
        """
        获取详细信息
        @基础信息     ORDER
        @货箱产品信息  ORDERVOL
        @文件信息     ORDERFILE
        @费用信息     ORDERCASH
        @路由轨迹     TRACKING
        :return:
        """
        cost_list = []
        track_list = []
        while not self.detail_ahc_queue.empty():
            order_id = self.detail_ahc_queue.get()
            report_nos = ['ORDERCASH', 'TRACKING']
            for report_type in report_nos:
                json_data = {
                    'reportno': report_type,
                    'opentype': 'find',
                    'colen': 'find',
                    'userquery1': order_id,
                    'userquery2': '%',
                }
                response = self.session.post(self.data_url, json=json_data, verify=False)
                data_list = response.json()
                if not data_list:
                    continue
                if report_type == 'ORDERCASH':
                    # 费用类型 清关手续费   运费
                    cost_list.extend(data_list)

                else:
                    data_list = self.etl_track_data(data_list)
                    track_list.append(data_list)

        self.tidb.insert_data(ods_scg_wld_logistics_ahc_cost_table,
                              ods_scg_wld_logistics_ahc_cost_i_d_field_list,
                              cost_list)
        self.tidb.insert_data(ods_scg_wld_logistics_ahc_track_table,
                              ods_scg_wld_logistics_ahc_track_i_d_field_list,
                              track_list)
        logger.info(f'快驿通-费用信息数据同步{len(cost_list)}完成')
        logger.info(f'快驿通-路由轨迹数据同步{len(track_list)}完成')

    def del_ahc_data(self):
        """
        清空 ahc 近 3个月的数据
        订单起始时间 和终止时间  后台筛选存在问题
        :return:
        """
        sql = f"delete from ods_prod.ods_scg_wld_logistics_ahc_i_d WHERE dt>='{self.start_date}' and dt<='{self.end_date}'"
        self.tidb.commit_sql(sql)
        logger.info("删除 快驿通数据 90天成功")

    def main(self):
        self.init_logistic('AHC')
        access_token = self.get_AccessToken()
        if not access_token:
            return
        self.init_headers(access_token)
        self.get_inbound_orders()
        self.get_detail_orders()


if __name__ == "__main__":
    ahc = CrawlerAhcLogisticData()
    ahc.main()
