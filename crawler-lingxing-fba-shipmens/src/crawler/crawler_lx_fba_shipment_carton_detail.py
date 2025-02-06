# _*_ coding: utf-8 _*_
# @Time : 2024/8/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-fba-shipmens
# @Desc : 领星-FBA货件-货件详情

from digiCore.utils.carwler_util import crawl
from loguru import logger

from model.fba_shipment_carton import ods_gsm_lx_fba_shipment_carton_i_h, ods_gsm_lx_fba_shipment_carton_i_field_list
from src.crawler import CrawlerBase


class CrawlerLXFbaShipmentCartonDetail(CrawlerBase):

    def __init__(self):
        super().__init__()
        self.ism_id_list = []
        self.shipment_detail_list = []

    def init_params(self):
        """
        初始化请求参数
        """
        sql = '''
        SELECT
          SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX( shipment_id_list,',',2),',',-1),':',-1)
            AS ism_id
        FROM
            ods_prod.ods_gsm_lx_shipment_ship_order_i_d
        where status != 3 and dt >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 4 WEEK), '%Y%m%d') 
        '''
        result = self.tidb_ob.query_list(sql)
        self.ism_id_list = [int(one.get("ism_id")) for one in result if int(one.get("ism_id"))]
        logger.info(f'FBA货件-货件详情-任务初始化完成：: {len(self.ism_id_list)}')

    def get_shipment_detail(self):
        """
        获取货件纸箱详情数据
        """
        while True:
            if not self.ism_id_list:
                break

            ism_id = self.ism_id_list.pop()
            url = f'https://erp.lingxing.com/api/fba_shipment/getCartonDetail?id={ism_id}'
            response = self.lx_api.lx_api_get(url)
            data = response.get('data')
            if not data:
                logger.error(f'{ism_id}--{response}')
                return
            data.pop('box_commit_result')
            data.pop('box_list')
            data.pop('carton_info')
            data.pop('data_shipped')
            data.pop('shipment_accesses')
            data.pop('shipment_info')
            self.shipment_detail_list.append(data)

    def main(self):
        """
        启动程序
        :return:
        """
        self.init_params()
        crawl(func=self.get_shipment_detail,max_workers=5)

        if self.shipment_detail_list:
            self.tidb_ob.insert_data(ods_gsm_lx_fba_shipment_carton_i_h,
                                     ods_gsm_lx_fba_shipment_carton_i_field_list,
                                     self.shipment_detail_list)
            logger.info(f"FBA货件详情数据保存完成：{len(self.shipment_detail_list)}")


if __name__ == '__main__':
    c = CrawlerLXFbaShipmentCartonDetail()
    c.main()
