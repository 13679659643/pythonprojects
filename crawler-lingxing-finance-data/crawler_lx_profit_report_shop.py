# -*- coding: utf-8 -*-
# @Time    : 2023/8/17 15:07
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    : 
# @Software:
import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from digiCore import Decorate
from digiCore.model import WebEnum
from loguru import logger

from common_resources import CrawlerBase
from db_model import ods_fc_gad_lx_profit_report_shop_i_d, ods_fc_gad_lx_profit_report_shop_i_d_field_list, \
    profit_report_shop_db_table
from settings import report_shop_url


class CrawlerProfitReportShopData(CrawlerBase):


    def get_date(self):
        """
        获取当月月末，上月月初日期
        :return:
        """
        now = datetime.now()

        # 获取上月月初日期
        last_month = now - relativedelta(months=1)
        start_date = datetime(last_month.year, last_month.month, 1).strftime('%Y-%m-%d')

        # 获取下月月初日期
        next_month = now + relativedelta(months=1)
        first_day_of_next_month = next_month.replace(day=1)
        # 获取本月的月末日期
        end_date = (first_day_of_next_month - relativedelta(days=1)).strftime('%Y-%m-%d')

        return start_date, end_date

    @Decorate.def_retry(msg="请求利润报表（订单）接口失败，正在重试！")
    def get_response(self, start_date, end_date, offset=0, length=1000, _code=1):
        """
        用于请求利润报表（订单）货件的数量
        :return:
        """
        json_data = {
            'startDate': start_date,
            'endDate': end_date,
            'offset': offset,
            'length': length,
            'mids': [],
            'sids': [],
            'currencyCode': '',
            'sellerPrincipalUids': [],
            'sortField': 'totalSalesQuantity',
            'sortType': 'desc',
            'isDisplayByDate': 'month',
            'version': None,
            'listingTagIds': [],
            'isMonthly': True,
            'req_time_sequence': '/bd/profit/report/report/seller/list$$3',
            'orderStatus': 'All',
        }
        response = self.post(report_shop_url, json_data)
        code = response.get("code")
        if int(code) != _code:
            return {}
        return response

    def original_to_format_key(self, order_data_list: list, table_dict: dict):
        """
        将读取出来的原始数据的key更换为格式化之后的key，并去多余key。
        :return:
        """
        new_data_list = []
        for data in order_data_list:
            # 找出原始数据中不存在的字段
            diff_keys = set(table_dict.keys()) - set(data.keys())
            new_item = {table_dict.get(k, k): str(v) for k, v in
                        data.items()
                        if k in table_dict}
            # 对不存在的字段进行赋值
            for key in diff_keys:
                if key == "dt":
                    continue
                new_item[table_dict[key]] = "None"
            new_data_list.append(new_item)
        return new_data_list

    def etl_data_list(self, response):
        data_list = []
        records_list = response.get('data')['records']
        for data in records_list:
            data['dt'] = data['postedDateLocale'].replace('-', '')
            data['otherFeeStr_1024469'] = next((item['feeAllocation'] for item in data['otherFeeStr'] if str(item['otherFeeTypeId']) == '1024469'), 0) if data['otherFeeStr'] != None else 0
            data['otherFeeStr'] = json.dumps(data['otherFeeStr'], ensure_ascii=False)
            del data['sellerPrincipalRealname']
            data_list.append(data)
        new_data_list = self.original_to_format_key(data_list, ods_fc_gad_lx_profit_report_shop_i_d_field_list)
        return new_data_list

    def save_tidb(self, data_list, start_date):
        # 删除历史数据
        delete_sql = f"""DELETE FROM {profit_report_shop_db_table} 
        where DATE_FORMAT('{start_date}', '%Y%m') >= DATE_FORMAT(DATE_ADD(CURRENT_DATE, INTERVAL -1 MONTH), '%Y%m')"""
        self.tidb_ob.commit_sql(delete_sql)
        logger.info(f"删除 利润报表-店铺数据  dt>={start_date}")
        # 同步最新数据
        self.tidb_ob.commit_sql(ods_fc_gad_lx_profit_report_shop_i_d)
        self.tidb_ob.insert_data(profit_report_shop_db_table, ods_fc_gad_lx_profit_report_shop_i_d_field_list.values(),
                                 data_list)
        logger.info(f"同步上月与本月，利润报表-店铺数据成功，数量 {len(data_list)} 条")

    def main(self):

        start_date, end_date = self.get_date()
        response = self.get_response(start_date, end_date)
        data_list = self.etl_data_list(response)
        self.save_tidb(data_list, start_date)
        return WebEnum.STATUS_SUCCESS


if __name__ == "__main__":
    cprsd = CrawlerProfitReportShopData()
    cprsd.main()
