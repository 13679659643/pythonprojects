# -*- coding: utf-8 -*-
# @Time    : 2024/12/26 17:35
# @Author  : Night
# @File    : dim_gsm_yida_non_amz_vis_sku_i_manual.py.py
# @Description:
from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("BD6-唯品会-sku  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("BD6-唯品会-sku  表数据更新完成！")

    def yida_data_to_tidb(self, config, combined_dict, yida_table_data):
        """
        将宜搭的表单数据保存到tidb数仓
        """
        db_table = config.get('tidb_table_name')
        field_list = [v for k, v in combined_dict.items()]
        data_list = yida_table_data
        field_list = ['sku', 'manager']
        self.tidb_ob.insert_data(db_table, field_list, data_list)


if __name__ == '__main__':
    form_uuid = 'FORM-A75C3AA2892848FE8BA4925AD8D11189UDCF'
    i = Sync()
    i.main(form_uuid)
    '''
    {"sku":"款号"}
    '''
