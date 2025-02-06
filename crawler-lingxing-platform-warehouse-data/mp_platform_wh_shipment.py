# _*_ coding: utf-8 _*_
# @Time : 2024/3/25
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-platform-warehouse-data
# @Desc : 领星-多平台-平台仓-待发货
from loguru import logger

from common_resource import Base
from db_model import ods_gsm_lx_mp_platform_wh_shipment_i_h, ods_gsm_lx_mp_platform_wh_shipment_field_list
from settings import mp_wh_shipment_url


class MpPlatformWHShipment(Base):
    """
    用于物流降本项目
    """

    def __init__(self):
        super().__init__()

        self.json_data = {
            'searchField': 1,
            'pickingStatus': '',
            'timeField': 2,
            'platformCodes': ['10008', '10002'],
            'offset': 0,
            'length': 50,
            'req_time_sequence': '/mp-platform-warehouse-api/api/shippingList/list$$4',
        }

    def customer_task(self):
        """
        采集数据
        """
        _lists = []
        pages = 1
        while pages > 0:
            response = self.post(
                url=mp_wh_shipment_url,
                data=self.json_data
            )
            data = response.get('data')
            _list = data.get('list')
            for one in _list:
                one.pop('goodExtDetails')
                one.pop('logisticsDetails')
                one['dt'] = one.get('gmtCreate').split(' ')[0].replace('-', '')
            _lists += _list
            total = data.get('total')
            pages = (int(total) - 1) // 50 + 1
            if int(pages):
                self.json_data['offset'] += 50
                pages -= 1
            else:
                break
        return _lists

    def main(self):

        _lists = self.customer_task()
        if not _lists:
            return
        self.tidb_ob.insert_data(ods_gsm_lx_mp_platform_wh_shipment_i_h,
                                 ods_gsm_lx_mp_platform_wh_shipment_field_list,
                                 _lists)
        logger.info(f"领星-平台仓发货单-列表数据采集完成：{len(_lists)} !")


if __name__ == '__main__':
    m = MpPlatformWHShipment()
    m.main()
