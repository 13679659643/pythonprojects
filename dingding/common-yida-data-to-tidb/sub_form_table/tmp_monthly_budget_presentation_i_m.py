# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 月度预算提报

from datetime import datetime

from loguru import logger

from common import BaseSync
from settings import bus_category


class Sync(BaseSync):

    def check_month(self, formData):
        """
        判断文件创建的日期是否属于本月
        """
        timestamp = formData.get('dateField_licip9q6')
        if not timestamp:
            return False
        application_month = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')

        # 将时间戳转换为datetime对象
        current_date = datetime.now().strftime('%Y-%m-%d')

        is_current_month = True if application_month >= current_date else False
        return is_current_month

    def format_data(self, formData, combined_dict):
        """
        formData数据嵌套了子表
        需要将子表中的数据取出

        dt和date使用相同的日期，dt格式话为yymmdd
        """
        data_list = []
        data = {}
        data['applicant'] = formData['textField_licip9pn']  # 申请人
        data['bus'] = formData['departmentSelectField_licikynk'][0]  # 申请部门
        timestamp = formData['dateField_licip9q6']
        application_month = datetime.fromtimestamp(timestamp / 1000).strftime('%Y%m')
        data['y_m'] = application_month  # 申请月份
        tableField = formData['tableField_licip9po']
        for one in tableField:
            updated_data = {combined_dict[k]: one[k] for k in combined_dict if k in one}
            category = updated_data.get('category')
            if not category:
                updated_data['category'] = bus_category.get(data.get('bus'))
            updated_data.update(data)
            data_list.append(updated_data)
        return data_list

    def get_yida_table_data(self, ding_core, combined_dict):
        """
        获取宜搭表单数据
        """
        yida_table_data = []
        page_number = 1
        while True:
            form_table_data = ding_core.get_form_table_data(page_number)
            if not form_table_data:
                break
            for one in form_table_data:
                formData = one.get('formData')
                is_current_month = self.check_month(formData)
                if not is_current_month:
                    continue

                data_list = self.format_data(formData, combined_dict)
                yida_table_data += data_list
            page_number += 1
        return yida_table_data

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("月度预算提报-临时表  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("月度预算提报-临时表  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-LK766AC1LO9BYYA5DHWNX8VF3NXL2RM5KICIL0'
    i = Sync()
    i.main(form_uuid)
    '''
    {"advertising_cost": "预算提报列表-广告费用", "applicant": "申请人", "bus": "申请人部门",
     "deliverr_budget": "预算提报列表-deliverr预算", "distribution_cost": "预算提报列表-配送费用",
     "distribution_cost_ratio": "预算提报列表-配送费用占比", "gross_profit_amount_target": "预算提报列表-毛利额目标",
     "gross_profit_rate_target": "预算提报列表-毛利率目标", "gross_profit_threshold": "预算提报列表-毛利额红线",
     "marketing_cost": "预算提报列表-营销费用", "marketing_cost_ratio": "预算提报列表-营销费用占比",
     "notes": "预算提报列表-备 注", "other_budgets": "预算提报列表-其他预算",
     "other_promotions": "预算提报列表-其它推广", "product_cost": "预算提报列表-货品成本",
     "product_cost_ratio": "预算提报列表-货品成本占比", "product_sales_volume": "预算提报列表-商品销量",
     "product_subsidies": "预算提报列表-商品补贴", "replenishment_cost": "预算提报列表-补单费用",
     "replenishment_principal": "预算提报列表-补单本金", "sales_revenue_target": "预算提报列表-销售额目标",
     "store_name": "预算提报列表-店铺名称","category":"预算提报列表-品类", "vine_evaluation_cost": "预算提报列表-VINE评费用",
     "warehousing_cost": "预算提报列表-仓储费用", "warehousing_cost_ratio": "预算提报列表-仓储费用占比",
     "y_m": "申请月份"}
    '''
