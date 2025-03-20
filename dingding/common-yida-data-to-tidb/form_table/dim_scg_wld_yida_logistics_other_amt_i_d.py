# _*_ coding: utf-8 _*_
# @Time : 2024/4/19
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 物流关税填报


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
                init_data = {
                    "shipment_id": "",
                    "customs_clearance_fee": 0,
                    "estimated_duty_fee": 0,
                    "compensation_fee": 0,
                    "customs_declaration_fee": 0,
                    "freight_compensation_fee": 0,
                    "lost_shipping_fee": 0,
                    "value_compensation_fee": 0,
                }
                formData = one.get('formData')
                # 同时过滤formData并替换键
                updated_data = {combined_dict[k]: formData[k] for k in combined_dict if k in formData}
                init_data.update(updated_data)
                yida_table_data.append(init_data)
            page_number += 1
            logger.info(f'存在多页，正在采集第 {page_number} 页数据！')
        return yida_table_data

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("物流降本-物流关税填报-杨洋  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("物流降本-物流关税填报-杨洋  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-8A4B49B7BAEC49209DFA473CD8E425C1SU1C'
    i = Sync()
    i.main(form_uuid)
    '''
    {"id": "id", "inner_account_id": "inner_account_id", "kingdee_bank_account": "kingdee_bank_account",
     "kingdee_customer_number": "kingdee_customer_number", "kingdee_department_name": "kingdee_department_name",
     "kingdee_department_number": "kingdee_department_number", "kingdee_org": "kingdee_org",
     "kingdee_settlement_mode": "kingdee_settlement_mode", "platform_account": "platform_account",
     "sale_department_number": "sale_department_number", "shop_name": "shop_name"}
    '''
