# -*- coding: utf-8 -*-
# @Time    : 2024/12/26 9:19
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:

from digiCore.db.redis.core import RedisDao
from digiCore.db.tidb.core import TiDBDao
from digiCore.lingxing.crawler_http import RequestHelper
from loguru import logger
from db_model import dim_gsm_lx_multi_platform_temu_sale_field_list, dim_gsm_lx_multi_platform_temu_sale


class LxMutilChannelTemu:
    def __init__(self):
        self.tidb_ob = TiDBDao()
        self.redis_ob = RedisDao()
        self.lx_api = RequestHelper()
        self.temu_detail_list = []

    @staticmethod
    def init_json_data():
        """
        初始化response json_data请求参数
        """
        json_data = {
            'brandIds': [],
            'categoryIds': [],
            'offset': 0,
            'length': 200,
            'pairingStatus': '',  # 1：已配对 2：未配对
            'searchField': '1',
            'status': '',  # 2:正常 0：删除
            'storeIds': [],
            'searchSingleValue': '',
            'searchValues': [],
            'req_time_sequence': '/mp-listing-api/api/temu/queryPage$$520',
        }
        logger.info(f"lx多平台Temu在线商品 创建成功！")
        return json_data

    def get_temu_sale_data(self, json_data):
        """
        获取多平台-销售-temu在线商品页面数据
        """
        base_url = 'https://gw.lingxingerp.com/mp-listing-api/api/temu/queryPage'
        temu_detail_list = []
        while True:
            response = self.lx_api.lx_api_post(base_url, json_data)
            data_list = response["data"]["list"]
            temu_detail_list += data_list
            if not data_list:
                break
            json_data["offset"] += 200
        return temu_detail_list

    def etl_data_list(self, temu_detail_list):
        """
        处理获取到的数据
        :param temu_detail_list:
        :return:
        """
        for item in temu_detail_list:
            new_item = {field: item.get(field) for field in dim_gsm_lx_multi_platform_temu_sale_field_list if
                        field not in ['warehouseId', 'warehouseName', 'supplyPriceList']}
            if item.get('wareHouseDataList'):
                new_item['warehouseId'] = item['wareHouseDataList'][0].get('warehouseId')
                new_item['warehouseName'] = item['wareHouseDataList'][0].get('warehouseName')
            if item.get('supplyPriceList'):
                new_item['supplyPriceList'] = item['supplyPriceList'][0].get('currency') + str(
                    item['supplyPriceList'][0].get('price'))
            else:
                new_item['supplyPriceList'] = item['supplyPriceList']
            self.temu_detail_list.append(new_item)

    def tidb_save(self):
        """
        :param data_list:
        :param db: 表对象
        数据同步到Tidb
        :return:
        """
        self.tidb_ob.insert_data(dim_gsm_lx_multi_platform_temu_sale,
                                 dim_gsm_lx_multi_platform_temu_sale_field_list,
                                 self.temu_detail_list)

    def main(self):
        json_data = self.init_json_data()
        temu_detail_list = self.get_temu_sale_data(json_data)
        self.etl_data_list(temu_detail_list)
        self.tidb_save()
        logger.info(f"lx多平台Temu在线商品数据采集完成：{len(self.temu_detail_list)}")


if __name__ == '__main__':
    lx = LxMutilChannelTemu()
    lx.main()
