# _*_ coding: utf-8 _*_
# @Time : 2024/4/8
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 宜搭-销售目标表
from datetime import datetime

from dateutil.relativedelta import relativedelta
from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def format_data(self, original_data):
        """
        将单条数据进行拆分，按照本月、下月、下下月分拆为3条
        """
        dt_timestamp = original_data['dt']
        # 将毫秒转换为秒
        timestamp = dt_timestamp / 1000

        # 将时间戳转换为datetime对象
        date = datetime.fromtimestamp(timestamp)

        # 当前月份
        current_month = date.strftime('%Y%m')

        # 下个月
        next_month_date = date + relativedelta(months=1)
        next_month = next_month_date.strftime('%Y%m')

        # 下下个月
        month_after_next_date = date + relativedelta(months=2)
        month_after_next = month_after_next_date.strftime('%Y%m')
        data_list = []

        if current_month != datetime.now().strftime('%Y%m'):
            # 当前时间不等于当月生效时间，过滤掉
            return data_list

        for one in [("this_m", current_month), ("next_m", next_month), ("last_m", month_after_next)]:
            data = {}
            data["dt"] = one[1]
            data["bus"] = original_data["bus"]
            data["original_spu_color"] = original_data["original_spu_color"]
            data["nation"] = original_data["nation"]
            data["wh"] = original_data["wh"]
            data["manger"] = original_data["manger"]
            data["original_spu"] = original_data["original_spu"]
            data["original_color"] = original_data["original_color"]
            data["brand"] = original_data["brand"]
            data["sales_target"] = original_data.get(one[0], 0)
            data_list.append(data)
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
                original_data = {combined_dict[k]: formData[k] for k in combined_dict if k in formData}
                yida_table_data += self.format_data(original_data)
            page_number += 1
            logger.info(f'正在采集第{page_number}页！')
        return yida_table_data

    def yida_data_to_tidb(self, config, combined_dict, yida_table_data):
        """
        将宜搭的表单数据保存到tidb数仓
        """
        db_table = config.get('tidb_table_name')
        field_list = [k for k, v in yida_table_data[0].items()]
        data_list = yida_table_data
        self.tidb_ob.insert_data(db_table, field_list, data_list)

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("宜搭-销售目标表  正在更新数据！")
        self.sync(form_uuid)
        logger.info("宜搭-销售目标表  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-62BA0789188C49FCB17151380BA958EC1IS6'
    i = Sync()
    i.main(form_uuid)
    '''
    {"dt": "生效月份", "bus": "事业部", "original_spu_color": "SPU颜色", 
    "nation": "地区", "wh": "warehouse","manger":"负责人","original_spu":"SPU",
    "original_color": "颜色","brand": "品牌","this_m": "本月","next_m": "下月","last_m": "下下月"}
    '''
