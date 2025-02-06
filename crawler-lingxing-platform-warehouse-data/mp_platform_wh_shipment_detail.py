# _*_ coding: utf-8 _*_
# @Time : 2024/3/25
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-platform-warehouse-data
# @Desc :
import json

from loguru import logger

from common_resource import Base
from db_model import ods_gsm_lx_mp_platform_wh_shipment_detail_i_h, ods_gsm_lx_mp_platform_wh_shipment_detail_field_list


class MpPlatformWHShipmentDetail(Base):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://gw.lingxingerp.com/mp-platform-warehouse-api/api/shippingList/getShippingListByCode?shippingListCode={shippingListCode}'

    def query_shipment_id(self):
        """
        查询待发货列表页信息
        """
        sql = "SELECT dt,shippingListCode FROM `ods_prod`.`ods_gsm_lx_mp_platform_wh_shipment_i_h` where dt >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 2 WEEK ), '%Y%m%d')"
        shipping_code_list = self.tidb_ob.query_list(sql)
        return shipping_code_list

    def customer_task(self, shipping_code_list):
        """
        请求详情页数据
        """
        shipment_detail_list = []
        for shipping_code in shipping_code_list:
            shippingListCode = shipping_code.get('shippingListCode')
            dt = shipping_code.get('dt')
            url = self.base_url.format(shippingListCode=shippingListCode)
            response = self.get(url)
            data = response.get('data')
            goodsExtDetails = data.get('goodsExtDetails')
            for one in goodsExtDetails:
                one['dt'] = dt
                one['shippingListCode'] = shippingListCode
                one['specInfo'] = json.dumps(one['specInfo'])
                shipment_detail_list.append(one)
        return shipment_detail_list

    def main(self):
        shipping_code_list = self.query_shipment_id()

        shipment_detail_list = self.customer_task(shipping_code_list)

        self.tidb_ob.insert_data(ods_gsm_lx_mp_platform_wh_shipment_detail_i_h,
                                 ods_gsm_lx_mp_platform_wh_shipment_detail_field_list,
                                 shipment_detail_list)

        logger.info(f"领星-平台仓发货单-详情数据采集完成：{len(shipment_detail_list)} !")

if __name__ == '__main__':
    s = MpPlatformWHShipmentDetail()
    s.main()