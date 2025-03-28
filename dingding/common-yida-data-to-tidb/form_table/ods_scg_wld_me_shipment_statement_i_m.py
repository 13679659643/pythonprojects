# _*_ coding: utf-8 _*_
# @Time : 2024/5/9
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc :
from datetime import datetime

from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def format_data(self, formData, combined_dict):
        """
        formData数据嵌套了子表
        需要将子表中的数据取出

        dt和date使用相同的日期，dt格式话为yymmdd
        """
        data_list = []
        m_data = list(formData.values())[0]
        for m_one in m_data:
            updated_data = {}
            # 同时过滤formData并替换键
            for k in combined_dict:
                if k not in m_one:
                    continue
                updated_data[combined_dict[k]] = m_one[k]
            timestamp = updated_data['date']
            date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            updated_data['date'] = date
            data_list.append(updated_data)
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
                updated_data = {combined_dict[k]: formData[k] for k in combined_dict if k in formData}

                timestamp = updated_data['delivery_date']
                delivery_date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y%m%d')
                updated_data['delivery_date'] = delivery_date

                timestamp = updated_data['reconciliation_month']
                reconciliation_month = timestamp.split(' ')[0].replace('-','')
                updated_data['reconciliation_month'] = reconciliation_month

                updated_data['reconciliation_personnel'] = ",".join(updated_data['reconciliation_personnel'])

                yida_table_data.append(updated_data)
            page_number +=1
        return yida_table_data

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("仓储物流-财务货件对账表  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("仓储物流-财务货件对账表  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-B89DAC8C77124259BE1ECA125BD802713R44'
    i = Sync()
    i.main(form_uuid)
    '''
    {"delivery_date": "发货日期", "shipment_id": "货件单号", "reconciliation_month": "对账月份","is_check":"是否查验","reconciliation_personnel":"对账人员"}
    '''