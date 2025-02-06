# _*_ coding: utf-8 _*_
# @Time : 2024/8/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-fba-shipmens
# @Desc :
from digiCore.utils.carwler_util import crawl
from loguru import logger

from model.lx_shipment_kanban import ods_scg_wld_lx_shipment_kanban_item, ods_scg_wld_lx_shipment_kanban_item_field_list
from src.crawler import CrawlerBase


class LxShipmentKanbanItem(CrawlerBase):

    def __init__(self):
        super().__init__()
        self.url_list = []
        self.shipment_kanban_item_list = []

    def init_task(self):
        """
        初始化请求参数
        """
        sql = "SELECT shipment_id,sid FROM `ods_prod`.`ods_scg_wld_lx_shipment_kanban_i_h` WHERE dt >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 3 Month ), '%Y%m%d')"
        shipment_id_list = self.tidb_ob.query_list(sql)
        url = ("https://erp.lingxing.com/api/fba_shipment/getDetailForShipment?"
               "search_field=sku&"
               "search_value=&"
               "search_field_time=shipment_time&"
               "shipment_id={}&sid={}&req_time_sequence=%2Fapi%2Ffba_shipment%2FgetDetailForShipment$$18")
        self.url_list = [url.format(one['shipment_id'], one['sid']) for one in shipment_id_list]
        logger.info(f"FBA货件看板详情-任务创建成功: {self.url_list}")

    def get_shipment_kanban_item(self):
        """
        获取看板页面数据
        """

        while True:
            if not self.url_list:
                break
            url = self.url_list.pop()
            response = self.lx_api.lx_api_get(url)
            shipment_id = response['shipment_id']
            item_list = response["item_list"]
            shipment_kanban_item = [{'shipment_id': shipment_id, **one} for one in item_list]
            self.shipment_kanban_item_list += shipment_kanban_item

    def main(self):

        self.init_task()
        crawl(func=self.get_shipment_kanban_item,max_workers=10)
        logger.info("crawler:FBA货件看板详情 任务消耗完成")
        if self.shipment_kanban_item_list:
            self.tidb_ob.insert_data(ods_scg_wld_lx_shipment_kanban_item,
                                     ods_scg_wld_lx_shipment_kanban_item_field_list,
                                     self.shipment_kanban_item_list)
            logger.info(f"FBA货件看板数据保存完成：{len(self.shipment_kanban_item_list)}")

if __name__ == '__main__':
    l = LxShipmentKanbanItem()
    l.main()