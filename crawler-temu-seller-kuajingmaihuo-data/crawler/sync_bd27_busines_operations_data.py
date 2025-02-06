# _*_ coding: utf-8 _*_
# @Time : 2025/1/6
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-temu-seller-kuajingmaihuo-data
# @Desc : 从BD27海外仓项目营销数据看板，采集共享表格数据
import re
from datetime import datetime

from digiCore.dingding.common import DingdingCommon
from loguru import logger

from db._tidb import TidbConnector
from models.dwd_gsm_bd27_busines_operations import OdsBD27BusinesOperations
from settings import operatorId
from dataclasses import asdict, fields


class SyncBusinessOperationsData:

    def __init__(self):
        self.table_id = 'b9Y4gmKWrP1v2A9rFozgYMDwJGXn6lpz'
        self.sheet_list = ['店1', '店2', '店3', '店4', '店5', '店6', '店7', '店8']
        self.tidb_ob = TidbConnector()
        self.dingding_api = DingdingCommon()

    def get_store_operations_data(self, sheet):
        """
        获取店铺活动填报数据
        :return:
        """
        last_row = self.dingding_api.get_online_last_row(table_id=self.table_id,
                                                         operatorId=operatorId,
                                                         sheets=sheet)
        if not last_row:
            return
        array_range = self.get_read_array_range(last_row)
        logistics_shipping = self.dingding_api.read_dingding_onlne_excel_data(
            table_id=self.table_id,
            array_range=array_range,
            operatorId=operatorId,
            sheets=sheet)
        return logistics_shipping

    def get_read_array_range(self, last_row):
        """
        获取读取数据的范围
        """
        if last_row > 302:
            array_range = f"A{last_row - 300}:T{last_row}"
        elif last_row == 1:
            array_range = f"A2:T2"
        else:
            array_range = f"A2:T{last_row}"
        return array_range

    def format_date(self, date_str):
        # 如果日期字符串为空或者只包含空格，返回空字符串或None
        if not date_str or date_str.isspace():
            date_str = ""
            return date_str

        if ' ' in date_str:
            date_str = date_str.split(' ')[0]
        # 定义不同的日期格式
        date_formats = [
            "%Y/%m/%d",  # 2024/04/01
            "%Y%m%d",  # 20240401
            "%Y-%m-%d"  # 2024-04-01
        ]
        # 尝试匹配和转换日期
        for date_format in date_formats:
            try:
                # 尝试按照给定的格式解析日期
                date_str_format = datetime.strptime(date_str, date_format)
                # 如果解析成功，按照YYYYMMDD的格式返回日期字符串
                date_str = date_str_format.strftime("%Y%m%d")
                return date_str
            except ValueError:
                # 如果解析失败，尝试下一个格式
                logger.error(f"{date_str}:日期格式错误！")
                continue

        # 如果所有格式都不匹配，返回None或者抛出异常
        return date_str

    def format_operations_data(self, store_operations_data):
        """
        清洗数据
        :param store_operations_data:
        :return:
        """
        operations_data_list = []
        for store_operation in store_operations_data:
            operations_data = OdsBD27BusinesOperations(
                dt=self.format_date(store_operation[7]),
                platform=store_operation[1],
                store_name=store_operation[2].replace('(', '（').replace(')', '）').replace(' ', ''),
                spu=store_operation[3],
                category=store_operation[4],
                activity_type=store_operation[5],
                registration_time=self.format_date(store_operation[6]),
                start_time=self.format_date(store_operation[7]),
                end_time=self.format_date(store_operation[8]),
                registration_qty=store_operation[9],
                declared_price=store_operation[10],
                cost_price=store_operation[11],
                activity_manager=store_operation[12],
                goods_cost=store_operation[13],
                shipping_cost=store_operation[14],
                delivery_fee=store_operation[15],
                return_exchange_cost=store_operation[16],
                storage_cost=store_operation[17],
                other_fees=store_operation[18],
                predicted_profit=store_operation[19]
            )
            operations_data_list.append(asdict(operations_data))
        return operations_data_list

    def save_operations_data(self, operations_data_list):
        """
        保存数据
        :param operations_data_list:
        :return:
        """
        self.tidb_ob.insert_data(
            db_table=OdsBD27BusinesOperations.__tablename__,
            field_list=[field.name for field in fields(OdsBD27BusinesOperations)],
            data_list=operations_data_list
        )

    def main(self):
        """
        启动程序
        :return:
        """
        while True:
            if not self.sheet_list:
                logger.info('数据采集完成，程序退出！')
                break

            sheet = self.sheet_list.pop()
            store_operations_data = self.get_store_operations_data(sheet)
            if not store_operations_data:
                logger.error(f'{sheet}:采集失败！重新插入队列！')
                self.sheet_list.append(sheet)
                continue

            operations_data_list = self.format_operations_data(store_operations_data)
            if operations_data_list:
                self.save_operations_data(operations_data_list)
                logger.info(f"{sheet}:保存成功！")


if __name__ == '__main__':
    s = SyncBusinessOperationsData()
    s.main()
