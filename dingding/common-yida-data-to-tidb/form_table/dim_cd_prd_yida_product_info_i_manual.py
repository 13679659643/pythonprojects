# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 商品信息表


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
                grade = updated_data.get('grade')
                if grade is None or grade == 'None' or grade == '':
                    grade = 'D'
                updated_data['grade'] = grade
                yida_table_data.append(updated_data)
            page_number += 1
        return yida_table_data


    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("商品信息表  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("商品信息表  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-4V966QC19O1EMJI6FAENK6KEUL75241KDW9ML7'
    i = Sync()
    i.main(form_uuid)