# _*_ coding: utf-8 _*_
# @Time : 2024/3/21
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-finance-data
# @Desc :
from datetime import datetime

from loguru import logger

from common_resources import CrawlerBase
from db_model import profit_report_statement_data_table, ods_fc_gad_lx_profit_msku_statement_i_d_field_list, \
    profit_report_staetment_cost_db_table, ods_gsm_lx_profit_msku_statement_cost_detail_i_d_field_list
from settings import report_msku_url, report_msku_queue, report_msku_cost_queue, report_msku_cost_url


class StatementProducerCrawler(CrawlerBase):
    """
    生产者，生产任务，插入到任务队列
    """

    def get_pages(self, date):
        """
        获取当天的任务页数
        """
        json_data = {
            'startDate': date,
            'endDate': date,
            'offset': 0,
            'orderStatus': "Disbursed",
            'length': 200,
            'searchField': 'seller_sku',
            'sortField': 'totalSalesQuantity',
            'sortType': 'desc'
        }
        response = self.post(report_msku_url, json_data)
        pages = response["data"]["pages"]
        return pages

    def get_task_list(self, now_date, pages):
        task_list = []
        for i in range(0, pages):
            json_data = {
                'startDate': now_date,
                'endDate': now_date,
                'offset': i * 200,
                'length': 200,
                'searchField': 'seller_sku',
                'sortField': 'totalSalesQuantity',
                'sortType': 'desc',
                'orderStatus': 'Disbursed',
            }
            task_list.append(json_data)
        return task_list

    def produce(self, date):
        """
        生产任务
        """
        logger.info(f"利润报表-msku维度 生成日期为:{date} 的任务！")
        pages = self.get_pages(date)
        task_list = self.get_task_list(date, pages)
        self.redis_ob.push_task(report_msku_queue, task_list)
        logger.info(f"利润报表-msku维度 插入任务队列： {len(task_list)} 条")


class StatementConsumerCrawler(CrawlerBase):
    """
    消费者，消费任务，结果存入数据库
    """
    all_data_list = []

    def extra_path(self, data, otherFeeStr):
        """
        针对返回的数据为空，都赋值为None
        """
        other_fee_map = {
            "其他费": "customized_other_fee",
            "直邮发货运费": "customized_direct_shipping_fee",
            "FBM订单发货成本": "customized_fbm_order_fee",
            "FBM订单退货成本": "customized_fbm_order_return_fee",
            "FBA广告费用调整": "customized_fba_adjustment_fee",
            "出清补贴": "customized_buyout_subsidy",
            "新品补贴": "customized_new_product_subsidy",
            "跌价准备金计提": "customized_provision_price",
            "跌价准备金回冲": "customized_provision_price_decreases",
            "特殊结算价差价补贴": "customized_settlement_price_difference_subsidy",
            "入境外仓出库操作费": "customized_inbound_warehouse_outbound_fees",
            "多平台头程回冲": "customized_multi_platform_headway_backflush",
            "多平台尾程回冲": "customized_multi_platform_tailrace_backflush",
            "多平台货本回冲": "customized_multi_platform_cost_backflush",
            "旺季仓储费补贴": "customized_subsidy_peak_storage_fees",
            "推广费补贴": "customized_subsidy_promotion_fees",
            "亚马逊卖家成长服务费": "customized_amazon_seller_growth_fee",
            "极致大单品抽成": "customized_hero_product_commission_fee"
        }
        # 创建一个新字典来存储更新后的值
        updated_fee_map = {value: 0 for value in other_fee_map.values()}
        if not otherFeeStr:
            return data.update(updated_fee_map)
        # 遍历otherFeeStr列表，更新other_fee_map中对应的值
        for fee in otherFeeStr:
            fee_name = fee['otherFeeName']
            if fee_name in other_fee_map:
                updated_fee_map[other_fee_map[fee_name]] = fee['feeAllocation']
        return data.update(updated_fee_map)

    def etl_data_list(self, records, task):
        data_list = []
        for data in records:
            data["dt"] = task.get('startDate').replace("-", "")
            otherFeeStr = data.get('otherFeeStr')
            self.extra_path(data, otherFeeStr)
            data_list.append(data)
        return data_list

    def save_data(self):

        self.tidb_ob.insert_data(profit_report_statement_data_table,
                                 ods_fc_gad_lx_profit_msku_statement_i_d_field_list,
                                 self.all_data_list)
        logger.info(f"利润报表-msku维度 数据保存完成！总计：{len(self.all_data_list)}")
        self.all_data_list.clear()

    def consume(self):
        """
        消费任务
        """
        while True:
            task = self.redis_ob.pop_task(report_msku_queue)
            if not task:
                break
            response = self.post(report_msku_url, task)
            data = response.get("data", [])
            if not data:
                continue
            records = data.get("records")
            data_list = self.etl_data_list(records, task)
            self.all_data_list += data_list


class StatementCostProducerCrawler(CrawlerBase):
    """
    生产者，生产任务，插入到任务队列
    """

    def get_profit_statement_msku(self, date):
        """
        获取距离当天days天的日期
        如果其他成本、头程成本、采购成本都为0，则无需采集
        """
        date_str = date.replace('-', '')
        sql = (f"select msku,dt,sid,currencyCode from ods_prod.ods_gsm_lx_profit_statement_msku_i_d "
               f"where cgTransportCostsTotal + cgOtherCostsTotal + cgPriceTotal != 0 and dt='{date_str}' and msku!='-'")
        msku_data = self.tidb_ob.query_list(sql)
        return msku_data

    def get_task_list(self, msku_data):
        task_list = []
        for cn_data in msku_data:
            date_str = datetime.strptime(cn_data['dt'], '%Y%m%d').strftime('%Y-%m-%d')
            json_data = {
                'startDate': date_str,
                'endDate': date_str,
                'offset': 0,
                'length': 200,
                'mids': [],
                'sids': [
                    cn_data['sid'],
                ],
                'currencyCode': cn_data['currencyCode'],
                'cids': [],
                'bids': [],
                'principalUids': [],
                'searchField': 'seller_sku',
                'searchValue': [],
                'sortField': 'totalSalesQuantity',
                'sortType': 'desc',
                'isDisplayByDate': '',
                'version': None,
                'listingTagIds': [],
                'isMonthly': False,
                'orderStatus': 'Disbursed',
                'msku': cn_data['msku'],
                'req_time_sequence': '/bd/profit/report/report/cost/details/get$$6',
            }
            task_list.append(json_data)
        return task_list

    def produce(self, date):
        """
        生产任务
        """
        logger.info(f"利润报表-msku维度-详情 生成日期为:{date} 的任务！")
        msku_data = self.get_profit_statement_msku(date)
        task_list = self.get_task_list(msku_data)
        self.redis_ob.push_task(report_msku_cost_queue, task_list)
        logger.info(f"利润报表-msku维度-详情 插入任务队列： {len(task_list)} 条")


class StatementCostConsumerCrawler(CrawlerBase):
    all_data_list = []

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
            "380101": ['cg_tansport_cost_amazon_sale_outstock_quantity',
                       'cg_tansport_cost_amazon_sale_outstock_amount'],
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

    def etl_data_list(self, data, task):
        item_data = {}
        other_cost = self.get_cgOtherCostsDetail_data(data['cgOtherCostsDetail'])
        cg_item = self.get_cgPriceDetail(data['cgPriceDetail'])
        cg_tansport_item = self.get_cgTransportCostsDetail(data['cgTransportCostsDetail'])
        item_data['dt'] = task['startDate'].replace('-', '')
        item_data['sid'] = task['sids'][0]
        item_data['msku'] = task['msku']
        item_data['currencyCode'] = task['currencyCode']
        item_data.update(other_cost)
        item_data.update(cg_item)
        item_data.update(cg_tansport_item)
        return item_data

    def save_data(self):
        self.tidb_ob.insert_data(profit_report_staetment_cost_db_table,
                                 ods_gsm_lx_profit_msku_statement_cost_detail_i_d_field_list,
                                 self.all_data_list)
        logger.info(f"利润报表-msku维度-详情 数据保存完成！总计：{len(self.all_data_list)}")
        self.all_data_list.clear()

    def consume(self):
        """
        消费任务
        """
        while True:
            task = self.redis_ob.pop_task(report_msku_cost_queue)
            if not task:
                break
            response = self.post(report_msku_cost_url, task)
            data = response.get("data", [])
            if not data:
                continue
            datas = data[0]
            item_data = self.etl_data_list(datas, task)
            self.all_data_list.append(item_data)
