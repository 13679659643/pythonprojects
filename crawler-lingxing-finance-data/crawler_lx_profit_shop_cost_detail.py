# _*_ coding: utf-8 _*_
# @Time : 2024/6/19
# @Author : 李仕春
# @Email ： scli@doocn.com
# @File : crawler-lingxing-finance-data
# @Desc : 获取利润报表店铺维度-费用明显数据
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from digiCore import Decorate
from loguru import logger

from common_resources import CrawlerBase
from db_model import ods_gsm_lx_profit_shop_cost_detail_i_d, ods_gsm_lx_profit_shop_cost_detail, \
    ods_gsm_lx_profit_shop_cost_detail_list
from settings import report_msku_cost_url


class CrawlerLxProfitShopCostDetail(CrawlerBase):

    def get_month_start_end(self, date_str):
        year, month = map(int, date_str.split('-'))
        # 月初日期
        month_start = datetime(year, month, 1).strftime('%Y-%m-%d')
        # 下个月的月初日期
        if month == 12:
            next_month_start = datetime(year + 1, 1, 1)
        else:
            next_month_start = datetime(year, month + 1, 1)
        # 月末日期
        month_end = (next_month_start - timedelta(days=1)).strftime('%Y-%m-%d')
        return month_start, month_end

    def get_profit_shop_list(self, y_m):
        """
        获取利润报表店铺维度，店铺列表数据
        """
        sql = f"""
        select sid,currencyCode from ods_prod.ods_gsm_lx_profit_report_store_i_d
        where dt = {y_m.replace('-', '')}
        group by sid
        """
        sid_list = self.tidb_ob.query_list(sql)
        return sid_list

    def get_response(self, month_start, month_end, month, sid_dict):

        json_data = {
            'startDate': month_start,
            'endDate': month_end,
            'offset': 0,
            'length': 200,
            'mids': [],
            'sids': [
                sid_dict.get('sid')
            ],
            'currencyCode': sid_dict.get('currencyCode'),
            'sellerPrincipalUids': [],
            'sortField': 'totalSalesQuantity',
            'sortType': 'desc',
            'isDisplayByDate': 'month',
            'version': None,
            'listingTagIds': [],
            'isMonthly': True,
            'displayByMonth': month,
            'req_time_sequence': '/bd/profit/report/report/cost/details/get$$1',
            'orderStatus': 'Disbursed'
        }
        response = self.post(url=report_msku_cost_url, data=json_data)
        return response

    def etl_data(self, response, month, sid_dict):
        item_data = {}
        data = response.get('data', [])[0]
        cgOtherCostsDetail = data.get('cgOtherCostsDetail', [])
        cgPriceDetail = data.get('cgPriceDetail', [])
        cgTransportCostsDetail = data.get('cgTransportCostsDetail', [])


        cg_price_data = self.get_cgPriceDetail(cgPriceDetail)
        cg_transport_cost_data = self.get_cgTransportCostsDetail(cgTransportCostsDetail)
        cg_other_cost_data = self.get_cgOtherCostsDetail_data(cgOtherCostsDetail)
        item_data['dt'] = month.replace('-', '')
        item_data['sid'] = sid_dict.get('sid')
        item_data['currency_code'] = sid_dict.get('currencyCode')
        item_data.update(cg_other_cost_data)
        item_data.update(cg_price_data)
        item_data.update(cg_transport_cost_data)
        return item_data

    def get_cgPriceDetail(self, cg_price_item):
        """
        采购成本
        """
        price_detail_map = {
            "202": ['cg_price_fba_amazon_quantity', 'cg_price_fba_amazon_amount'],
            "201": ['cg_price_fba_multichannel_quantity', 'cg_price_fba_multichannel_amount'],
            "215": ['cg_price_fba_remove_quantity', 'cg_price_fba_remove_amount'],
            "200": ['cg_price_fba_replacement_quantity', 'cg_price_fba_replacement_amount'],
            "220": ['cg_price_fba_stock_out_quantity', 'cg_price_fba_stock_out_amount'],
            "30": ['cg_price_fba_unsingle_return_quantity', 'cg_price_fba_unsingle_return_amount'],
            "25": ['cg_price_fba_stock_in_quantity', 'cg_price_fba_stock_in_amount'],
            "31": ['cg_price_fba_single_return_quantity', 'cg_price_fba_single_return_amount'],
            "380101": ['cg_price_amazon_sale_outstock_quantity', 'cg_price_amazon_sale_outstock_amount'],
        }
        # 创建一个新字典来存储更新后的值
        price_detail = {one: 0 for value in price_detail_map.values() for one in value}
        # 遍历otherFeeStr列表，更新other_fee_map中对应的值
        for fee in cg_price_item:
            typeName = fee['typeName']
            if typeName in price_detail_map:
                price_detail[price_detail_map[typeName][0]] = fee['quantity']
                price_detail[price_detail_map[typeName][1]] = fee['amount']
        return price_detail

    def get_cgTransportCostsDetail(self, cg_tansport_cost_item):
        """
        头程成本
        """
        tansport_cost_map = {
            "202": ['cg_tansport_cost_fba_amazon_quantity', 'cg_tansport_cost_amazon_amount'],
            "201": ['cg_tansport_cost_fba_multichannel_quantity', 'cg_tansport_cost_fba_multichannel_amount'],
            "215": ['cg_tansport_cost_fba_remove_quantity', 'cg_tansport_cost_fba_remove_amount'],
            "200": ['cg_tansport_cost_fba_replacement_quantity', 'cg_tansport_cost_fba_replacement_amount'],
            "220": ['cg_tansport_cost_fba_stock_out_quantity', 'cg_tansport_cost_fba_stock_out_amount'],
            "30": ['cg_tansport_cost_fba_unsingle_return_quantity', 'cg_tansport_cost_fba_unsingle_return_amount'],
            "25": ['cg_tansport_cost_fba_stock_in_quantity', 'cg_tansport_cost_fba_stock_in_amount'],
            "31": ['cg_tansport_cost_fba_single_return_quantity', 'cg_tansport_cost_fba_single_return_amount'],
            "380101": ['cg_tansport_cost_amazon_sale_outstock_quantity', 'cg_tansport_cost_amazon_sale_outstock_amount'],
        }
        # 创建一个新字典来存储更新后的值
        tansport_cost = {one: 0 for value in tansport_cost_map.values() for one in value}
        # 遍历otherFeeStr列表，更新other_fee_map中对应的值
        for fee in cg_tansport_cost_item:
            typeName = fee['typeName']
            if typeName in tansport_cost_map:
                tansport_cost[tansport_cost_map[typeName][0]] = fee['quantity']
                tansport_cost[tansport_cost_map[typeName][1]] = fee['amount']
        return tansport_cost

    def get_cgOtherCostsDetail_data(self, other_cost_item):
        """
        其他成本
        """
        other_cost_map = {
            '202': ['other_cost_fba_amazon_quantity', 'other_cost_fba_amazon_amount'],  # FBA亚马逊销售订单
            '201': ['other_cost_fba_multichannel_quantity', 'other_cost_fba_multichannel_amount'],  # FBA多渠道销售订单
            '215': ['other_cost_fba_remove_quantity', 'other_cost_fba_remove_amount'],  # FBA移除
            '200': ['other_cost_fba_replacement_quantity', 'other_cost_fba_replacement_amount'],  # FBA补发货销售
            '220': ['other_cost_fba_stock_out_quantity', 'other_cost_fba_stock_out_amount'],  # FBA盘点出库
            '30': ['other_cost_fba_unsingle_return_quantity', 'other_cost_fba_unsingle_return_amount'],  # FBA无源单销售退货
            '25': ['other_cost_fba_stock_in_quantity', 'other_cost_fba_stock_in_amount'],  # FBA盘点入库
            '31': ['other_cost_fba_single_return_quantity', 'other_cost_fba_single_return_amount'],  # FBA有源单销售退货
            '380101': ['other_cost_amazon_sale_outstock_quantity', 'other_cost_amazon_sale_outstock_amount']
            # 自发货亚马逊销售出库
        }
        # 创建一个新字典来存储更新后的值
        other_cost = {one: 0 for value in other_cost_map.values() for one in value}
        # 遍历otherFeeStr列表，更新other_fee_map中对应的值
        for fee in other_cost_item:
            typeName = fee['typeName']
            if typeName in other_cost_map:
                other_cost[other_cost_map[typeName][0]] = fee['quantity']
                other_cost[other_cost_map[typeName][1]] = fee['amount']
        return other_cost

    def save_tidb(self, data_list, month):
        sql = ods_gsm_lx_profit_shop_cost_detail_i_d.replace('\n', ' ')
        self.tidb_ob.commit_sql(sql)
        self.tidb_ob.insert_data(ods_gsm_lx_profit_shop_cost_detail, ods_gsm_lx_profit_shop_cost_detail_list,
                                 data_list)
        logger.info(f"{month} 利润报表-店铺cost明细 数据成功，数量 {len(data_list)} 条")

    def main(self):
        for i in [0, 1]:
            month = (datetime.now() - relativedelta(months=i)).strftime("%Y-%m")
            month_start, month_end = self.get_month_start_end(month)
            sid_list = self.get_profit_shop_list(month)
            item_list = []
            while sid_list:
                sid_dict = sid_list.pop(0)
                response = self.get_response(month_start, month_end, month, sid_dict)
                item_data = self.etl_data(response, month, sid_dict)
                item_list.append(item_data)
            self.save_tidb(item_list, month)

if __name__ == '__main__':
    clpsd = CrawlerLxProfitShopCostDetail()
    clpsd.main()