# _*_ coding: utf-8 _*_
# @Time : 2024/06/12
# @Author : night
# @Email ： night@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 非亚马逊-沃尔玛经营维度管理


from loguru import logger

from common import BaseSync
from datetime import datetime


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("沃尔玛经营维度管理  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("沃尔玛经营维度管理  表数据更新完成！")

    def format_data(self, original_data):
        data_list = []
        original_data['dt'] = datetime.fromtimestamp(original_data['dt'] / 1000).strftime('%Y%m')
        data_list.append(original_data)
        return data_list

    def get_yida_table_data(self, ding_core, combined_dict):
        """
        获取宜搭表单数据
        """
        yida_table_data = []
        page_number = 1
        while True:
            data_list = ding_core.get_form_table_data(page_number)
            if not data_list:
                break
            for one in data_list:
                formData = one.get('formData')
                # 同时过滤formData并替换键
                original_data = {combined_dict[k]: formData[k] for k in combined_dict if k in formData}
                yida_table_data += self.format_data(original_data)
            page_number += 1
            logger.info(f'正在采集第{page_number}页！')
        return yida_table_data


if __name__ == '__main__':
    form_uuid = 'FORM-C3C30E7EA73748D68EE1D3D9F8FDCC472EIT'
    i = Sync()
    i.main(form_uuid)
    '''
    {"dt": "经营结账时间", "store": "店铺名", "wfs_adjustments_fees": "WFS调整", "wfs_storage_fee": "WFS仓储费",
          "wfs_rc_inventory": "WFSRC仓库处理费", "platform_advertising_fees": "平台广告费",
          "logistics_amortize": "物流头程摊销费用", "deliverr_delivery_fee": "Deliverr配送费用",
          "deliverr_storage_fee": "Deliverr仓储费用", "depreciation_reserve": "跌价准备金"}
    '''
