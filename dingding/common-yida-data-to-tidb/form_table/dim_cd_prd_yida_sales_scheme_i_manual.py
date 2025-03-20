# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 销售方案更新表
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
                timestamp = updated_data['working_month']
                working_month = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                updated_data['working_month'] = working_month
                yida_table_data.append(updated_data)
            page_number += 1
        return yida_table_data

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("销售方案更新表  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("销售方案更新表  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-GI666T81NTRFZ1AX690AC967I7ZX3EO68FSOLJ7'
    i = Sync()
    i.main(form_uuid)
    '''
    {"local_color": "颜色", "local_spu": "货号", "sale_method": "销售方案", 
    "spu_color": "货号颜色", "working_month": "生效月份","bus":"事业部","wh":"仓库名称"}
    '''
