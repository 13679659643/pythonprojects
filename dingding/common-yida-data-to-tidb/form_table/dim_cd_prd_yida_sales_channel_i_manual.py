# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 销售渠道方式表
from datetime import datetime

from loguru import logger

from common import BaseSync


class Sync(BaseSync):

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
                updated_data = {combined_dict[k]: formData[k] for k in combined_dict if k in formData}
                timestamp = updated_data.get('effective_month')
                if not timestamp:
                    updated_data['effective_month'] = '1980-01-01'
                else:
                    effective_month = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                    updated_data['effective_month'] = effective_month
                yida_table_data.append(updated_data)
            page_number += 1
        return yida_table_data

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("销售渠道方式表  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("销售渠道方式表  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-OS566L91QB2EOGTNBAEJ09A3HINB31R57X9ML3'
    i = Sync()
    i.main(form_uuid)
    '''
    {"channel_sales_method": "渠道销售方式", "color": "颜色", "num": "序号", "sku_sales_method": "SKU销售方式",
     "style_code": "货号", "warehouse": "仓库","effective_month":"生效月份"}
    '''
