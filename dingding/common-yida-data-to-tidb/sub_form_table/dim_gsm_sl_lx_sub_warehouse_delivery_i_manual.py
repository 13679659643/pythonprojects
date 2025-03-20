# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 发货操作费 - 下线

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
                data_list = self.format_data(formData, combined_dict)
                yida_table_data += data_list
            page_number +=1
        return yida_table_data

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("发货操作费  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("发货操作费  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-HT866U91JM7EUSQ59382QCNXRBPK2W2UE8KML7'
    i = Sync()
    i.main(form_uuid)
    '''
    {"date": "子仓发货费用表-日期", "dept": "子仓发货费用表-部门", "odd_even_charges": "子仓发货费用表-单双费用",
     "shippend_type": "子仓发货费用表-发货操作费类型"}
    '''
