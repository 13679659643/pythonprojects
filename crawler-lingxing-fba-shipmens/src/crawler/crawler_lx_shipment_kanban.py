# _*_ coding: utf-8 _*_
# @Time : 2024/8/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-fba-shipmens
# @Desc : 采集FBA发货看板数据
from digiCore.utils.date_util import get_begin_end_date
from urllib.parse import urlencode

from loguru import logger

from model.lx_shipment_kanban import ods_scg_wld_lx_shipment_kanban, ods_scg_wld_lx_shipment_kanban_field_list
from src.crawler import CrawlerBase


class LXShipmentKanban(CrawlerBase):
    def __init__(self):
        super().__init__()


    def init_params(self):
        """
        初始化请求参数
        """
        start_date, end_date = get_begin_end_date(days=90, date_format="%Y-%m-%d")
        if start_date < "2024-04-01":
            start_date = "2024-04-01"
        params = {
            "reference_status": "",
            "search_field_time": "shipment_time",
            "search_field": "shipment_id",
            "start_date": start_date,
            "end_date": end_date,
            "offset": 0,
            "length": 200,
            "req_time_sequence": "/api/fba_shipment/getDisplayBoardForShipment$$70"
        }
        logger.info(f"FBA货件看板-任务创建成功！")
        return params

    def get_shipment_kanban_data(self, params):
        """
        获取看板页面数据
        """
        base_url = 'https://erp.lingxing.com/api/fba_shipment/getDisplayBoardForShipment?'
        shipment_kanban_list = []
        while True:
            query_string = urlencode(params)
            url = base_url + query_string
            response = self.lx_api.lx_api_get(url)
            data_list = response["list"]
            shipment_kanban_list += data_list
            if not data_list:
                break
            params["offset"] += 200
        return shipment_kanban_list

    def main(self):
        params = self.init_params()
        shipment_kanban_list = self.get_shipment_kanban_data(params)
        shipment_kanban_list_with_dt = [{'dt': one['shipment_sn_list'][0]['shipment_time'].replace('-', '') if one[
            'shipment_sn_list'] else '',
                                         **one} for one in
                                        shipment_kanban_list]

        self.tidb_ob.insert_data(ods_scg_wld_lx_shipment_kanban,
                                 ods_scg_wld_lx_shipment_kanban_field_list,
                                 shipment_kanban_list_with_dt)
        logger.info(f"FBA货件看板数据保存完成：{len(shipment_kanban_list_with_dt)}")

if __name__ == '__main__':

    l = LXShipmentKanban()
    l.main()