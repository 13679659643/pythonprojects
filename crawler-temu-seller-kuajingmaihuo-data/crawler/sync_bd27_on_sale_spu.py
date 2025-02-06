# _*_ coding: utf-8 _*_
# @Time : 2025/1/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-temu-seller-kuajingmaihuo-data
# @Desc : 同步BD27看板项目-在售SPU
from dataclasses import asdict, fields

from digiCore.dingding.common import DingdingCommon
from loguru import logger

from db._tidb import TidbConnector
from models.dim_gsm_bd27_on_sale_spu import OdsBD27OnSaleSPU
from settings import operatorId


class SyncBd27OnSaleSpu:
    def __init__(self):
        self.table_id = 'yQod3RxJKGoq4E92TpvjKoENJkb4Mw9r'
        self.sheet = 'Sheet1'
        self.tidb_ob = TidbConnector()
        self.dingding_api = DingdingCommon()

    def get_store_spu_data(self):
        """
        获取店铺活动填报数据
        :return:
        """
        last_row = self.dingding_api.get_online_last_row(table_id=self.table_id,
                                                         operatorId=operatorId,
                                                         sheets=self.sheet)
        if not last_row:
            return
        array_range = self.get_read_array_range(last_row)
        logistics_shipping = self.dingding_api.read_dingding_onlne_excel_data(
            table_id=self.table_id,
            array_range=array_range,
            operatorId=operatorId,
            sheets=self.sheet)
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

    def format_on_sale_data(self, store_spu_data):
        """
        清洗在售spu数据
        :param store_spu_data:
        :return:
        """
        data_list = []
        for store_spu in store_spu_data:
            spu_data = OdsBD27OnSaleSPU(
                spu=store_spu[0],
                status_text=store_spu[1],
                channel=store_spu[2]
            )
            data_list.append(asdict(spu_data))
        return data_list

    def save_on_sale_spu_data(self, on_sale_spu_data):
        """
        保存数据
        :param operations_data_list:
        :return:
        """
        self.tidb_ob.insert_data(
            db_table=OdsBD27OnSaleSPU.__tablename__,
            field_list=[field.name for field in fields(OdsBD27OnSaleSPU)],
            data_list=on_sale_spu_data
        )

    def main(self):
        """
        启动程序
        :return:
        """
        store_spu_data = self.get_store_spu_data()
        if not store_spu_data:
            logger.error(f'spu:采集失败！')
            return

        on_sale_spu_data = self.format_on_sale_data(store_spu_data)
        if on_sale_spu_data:
            self.save_on_sale_spu_data(on_sale_spu_data)
            logger.info(f"spu:保存成功！")


if __name__ == '__main__':
    s = SyncBd27OnSaleSpu()
    s.main()
