# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 非亚马逊业绩日报-手动填写
from datetime import datetime

from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def check_month(self, createTimeGMT):
        """
        判断文件创建的日期是否属于本月
        """
        extracted_date = datetime.strptime(createTimeGMT, '%Y-%m-%dT%H:%MZ').date()

        current_date = datetime.now().date()
        is_current_month = extracted_date.year == current_date.year and extracted_date.month == current_date.month
        return is_current_month

    def format_data(self, format_data_list, combined_dict):
        """
        formData数据嵌套了子表
        需要将子表中的数据取出

        dt和date使用相同的日期，dt格式话为yymmdd
        """
        data_list = []
        for m_one in format_data_list:
            updated_data = {}
            # 同时过滤formData并替换键
            for k in combined_dict:
                if k not in m_one:
                    continue

                # 格式化未填写的数据，设置为0
                if m_one[k] == '':
                    m_one[k] = 0

                updated_data[combined_dict[k]] = m_one[k]

            timestamp = updated_data['dt']
            date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            # 存在找不到字段的数据，设置为0
            updated_data['sale'] = updated_data.get('sale', 0)
            updated_data['spend'] = updated_data.get('spend', 0)
            updated_data['date'] = date
            updated_data['order_qty'] = updated_data.get('order_qty', 0)
            updated_data['refund_amt'] = updated_data.get('refund_amt', 0)
            updated_data['dt'] = date.replace('-', '')
            data_list.append(updated_data)
        return data_list

    def get_yida_table_data(self, ding_core, combined_dict):
        """
        获取宜搭表单数据
        """
        yida_table_data = []
        page_number = 1
        data_list = ding_core.get_form_table_data(page_number)
        for one in data_list:
            createTimeGMT = one.get('createTimeGMT')
            is_current_month = self.check_month(createTimeGMT)
            if not is_current_month:
                continue

            form_instance_id = one.get('formInstanceId')
            data_list = self.get_sub_table_data(ding_core,form_instance_id)
            format_data_list = self.format_data(data_list, combined_dict)
            yida_table_data += format_data_list
        return yida_table_data

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("非亚马逊业绩日报-手动填写  表正在更新数据！")
        config = self.get_config(form_uuid)
        access_token = self.get_dd_access_token()
        ding_core = self.init_ding_core(config, form_uuid, access_token)
        combined_dict = self.create_combined_dict(ding_core, config)
        yida_table_data = self.get_yida_table_data(ding_core, combined_dict)

        # 保存数据
        # combined_dict需要补一个date字段
        combined_dict['date'] = 'date'
        self.yida_data_to_tidb(config, combined_dict, yida_table_data)
        logger.info("非亚马逊业绩日报-手动填写  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-8Y866XB16AZDKOQ26V80V96N7BOY2D3PXL5ML0'
    i = Sync()
    i.main(form_uuid)
    '''
    {"bus": "业绩数据-事业部", "date": "业绩数据-日期", "dt": "业绩数据-日期", "order_qty": "业绩数据-订单",
     "manager": "业绩数据-负责人", "refund_amt": "业绩数据-退款额", "sale": "业绩数据-业绩",
     "store_name": "业绩数据-店铺名", "spend": "业绩数据-推广费", "uv": "业绩数据-UV"}
    '''
