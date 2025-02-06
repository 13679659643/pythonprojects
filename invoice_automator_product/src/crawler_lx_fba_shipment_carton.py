# -*- coding: utf-8 -*-
# @Time    : 2024/10/11 14:37
# @Author  : Night
# @File    : crawler_lx_fba_shipment_carton.py
# @Description:
import copy
from loguru import logger
import requests
from settings import fba_shipment_list_api, ods_gsm_lx_fba_shipment_carton_i_h, \
    ods_gsm_lx_fba_shipment_carton_i_field_list, dwd_scg_wld_lx_fba_shipment_box_detail_i_d, \
    dwd_scg_wld_lx_fba_shipment_box_detail_i_field_list, dwd_scg_wld_lx_fba_shipment_box_detail_item_i_d, \
    dwd_scg_wld_lx_fba_shipment_box_detail_item_i__field_d
from src.data_processing import DataProcessing
from digiCore.db.redis.core import RedisDao
from digiCore.common.decorate import def_retry


class CrawlerLXFbaShipmentCarton(DataProcessing):
    def __init__(self, shipment_id):
        super().__init__()
        self.shipment_id = shipment_id
        self.headers = {}
        self.redis_ob = RedisDao()

    def get_available_headers(self):
        """
        获取可用handers头
        :param headers: 请求头
        :return:
        """
        auth_token = self.redis_ob.get_lingxing_crawler_auth_token()
        headers = {
            "X-AK-Company-Id": "901140007506993664",
            "auth-token": auth_token
        }
        return headers

    @def_retry(msg="fba货件列表请求失败，正在重试！")
    def get_shipment_id(self):
        params = {
            'search_field_time': 'create_date',
            'is_sta': '',
            'is_awd': '',
            'ship_mode': '',
            'is_closed': '',
            'application_diff': '',
            'received_diff': '',
            'application_received_diff': '',
            'is_relate_packing_task_sn': '',
            'has_shipto_address': '',
            'is_shipto_diff': '',
            'is_add_tracking': '',
            'is_update_shipment_tracking_no': '',
            'search_field': 'shipment_id',
            'search_value': self.shipment_id,
            'is_relate_shipment': '',
            'is_uploaded_box': '',
            'offset': 0,
            'length': 20,
            'req_time_sequence': '/api/fba_shipment/showShipment_v2$$19'
        }
        json_data = requests.get(fba_shipment_list_api, headers=self.headers, params=params).json()
        if not json_data:
            logger.error(f'{self.shipment_id} 列表数据采集失败')
            return []
        ship_ids = [row['id'] for row in json_data['data']['list']]
        return ship_ids

    @def_retry(msg="fba货件详情请求失败，正在重试！")
    def get_shipment_detail(self, ism_id):
        """
        获取货件纸箱详情数据
        """
        url = f'https://erp.lingxing.com/api/fba_shipment/getCartonDetail?id={ism_id}'
        response = requests.get(url, headers=self.headers).json()
        data = response.get('data')
        if not data:
            logger.error(f'{ism_id}--{response}')
            return {}
        return data

    def elt_data(self, data):
        """
        处理装箱列表数据
        :param data:
        :return:
        """
        box_list = []
        # 创建数据的深拷贝，防止修改原数据
        data_copy = copy.deepcopy(data)
        carton_list = self.etl_carton_data(data_copy)
        data['dt'] = data['create_date'].split(" ")[0].replace("-", "")
        box_list.append(data)
        box_detail_list = self.etl_box_data(data)
        return carton_list, box_list, box_detail_list

    def etl_carton_data(self, data):
        """
        处理列表
        :param data:
        :return:
        """
        carton_list = []
        data_copy = copy.deepcopy(data)
        data_copy.pop('box_commit_result')
        data_copy.pop('box_list')
        data_copy.pop('carton_info')
        data_copy.pop('data_shipped')
        data_copy.pop('shipment_accesses')
        data_copy.pop('shipment_info')
        carton_list.append(data_copy)
        return carton_list

    def etl_box_data(self, data):
        """
        处理装箱详情数据
        :param data:
        :return:
        """
        box_detail_list = []
        data_copy = copy.deepcopy(data)
        shipment_id = data.get('shipment_id')
        for box in data_copy['box_list']:
            for item_li in box['item_list']:
                item_data = {}
                if int(item_li.get('num')) <= 0:
                    continue
                item_data['dt'] = data['dt']
                item_data['shipment_id'] = shipment_id
                item_data['box_id'] = box.get('box_id')
                item_data['length'] = box.get('length')
                item_data['width'] = box.get('width')
                item_data['height'] = box.get('height')
                item_data['weight'] = box.get('weight')
                item_data['packed'] = box.get('packed')
                item_data['fnsku'] = item_li.get('fnsku')
                item_data['msku'] = item_li.get('msku')
                item_data['quantity_shipped'] = item_li.get('quantity_shipped')
                item_data['exp_date'] = item_li.get('exp_date')
                item_data['num'] = item_li.get('num')
                box_detail_list.append(item_data)
        return box_detail_list

    def run(self):
        self.headers = self.get_available_headers()
        ship_ids = self.get_shipment_id()
        for ship_id in ship_ids:
            data = self.get_shipment_detail(ship_id)  # 货件详情
            if data:
                carton_list, box_list, box_detail_list = self.elt_data(data)
                # 货件详情
                self.tidb.insert_data(ods_gsm_lx_fba_shipment_carton_i_h,
                                      ods_gsm_lx_fba_shipment_carton_i_field_list,
                                      carton_list)
                # 货件详情装箱列表
                self.tidb.insert_data(dwd_scg_wld_lx_fba_shipment_box_detail_i_d,
                                      dwd_scg_wld_lx_fba_shipment_box_detail_i_field_list,
                                      box_list)
                # 货件详情装箱
                self.tidb.insert_data(dwd_scg_wld_lx_fba_shipment_box_detail_item_i_d,
                                      dwd_scg_wld_lx_fba_shipment_box_detail_item_i__field_d,
                                      box_detail_list)

                logger.info(f'-----{self.shipment_id} fba单 同步数据完成-----')


if __name__ == '__main__':
    c = CrawlerLXFbaShipmentCarton(shipment_id='FBA18HCKVK88')
    c.run()
