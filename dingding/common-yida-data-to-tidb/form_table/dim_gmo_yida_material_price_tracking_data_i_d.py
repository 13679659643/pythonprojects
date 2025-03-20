# _*_ coding: utf-8 _*_
# @Time : 2024-11-13
# @Author : 李仕春
# @Email ： scli@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 同步-数据集市-GMO总经办- DS-材料价格跟踪数据-录入
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
                # 做主键
                updated_data['form_instance_id'] = one.get('formInstanceId')
                # 处理生效日期格式
                timestamp = updated_data['effective_date']
                delivery_date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                updated_data['effective_date'] = delivery_date
                # 添加 创建日期，修改日期
                updated_data['creation_time'] = datetime.strptime(one.get('createTimeGMT'), '%Y-%m-%dT%H:%MZ').strftime(
                    '%Y-%m-%d %H:%M:%S')
                updated_data['change_time'] = datetime.strptime(one.get('modifiedTimeGMT'), '%Y-%m-%dT%H:%MZ').strftime(
                    '%Y-%m-%d %H:%M:%S')
                yida_table_data.append(updated_data)
            page_number += 1
            logger.info(f'存在多页，正在采集第 {page_number} 页数据！')
        return yida_table_data

    def yida_data_to_tidb(self, config, combined_dict, yida_table_data):
        """
        将宜搭的表单数据保存到tidb数仓
        """
        db_table = config.get('tidb_table_name')
        field_list = ['form_instance_id',
                      'creation_time',
                      'change_time',
                      'effective_date',
                      'member_name',
                      'spu',
                      'category',
                      'supplier_name',
                      'original_price',
                      'current_price',
                      'remake']
        self.tidb_ob.insert_data(db_table, field_list, yida_table_data)

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("材料价格跟踪数据  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("材料价格跟踪数据  表数据更新完成！")


if __name__ == '__main__':
    sync_obj = Sync()
    form_uuid = "FORM-BDEE81380F554A88BB3CF5D4AE5713AE3E8N"
    sync_obj.main(form_uuid)

    """
    {"member_name":"成员",
     "spu":"货号",
     "supplier_name":"供应商", 
     "original_price":"原价格",
     "current_price":"现价格",
     "effective_date":"生效日期",
     "remake":"备注",
     "category":"品类",
     "creation_time":"创建时间",
     "change_time":"修改时间"}
     """
