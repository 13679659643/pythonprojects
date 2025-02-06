# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 10:52
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import json

from loguru import logger

from base.crawler_base import CrawlerBase
from settings import orderlist_table_name


class MongoTidbTransferOrderList(CrawlerBase):
    """temu-跨境卖家中心-订单管理-订单列表-买家履约订单"""
    def __init__(self):
        super().__init__()

    @staticmethod
    def find_package_tracking_company(order, goodsId):
        """
        包裹信息转化为字典，便于存储
        """
        if not order['parentOrderMap']['waybillInfoList']:
            return {'packageSn': None, 'trackingNumber': None}
        for waybill_info in order['parentOrderMap']['waybillInfoList']:
            for related_goods_info in waybill_info['relatedGoodsInfoForAggregation']:
                if related_goods_info['goodsId'] == goodsId:
                    return {'shipCompanyName': waybill_info['shipCompanyName'],
                            'packageSn': waybill_info['packageSn'],
                            'trackingNumber': waybill_info['trackingNumber'],
                            }
        return {'packageSn': None, 'trackingNumber': None}

    @staticmethod
    def sum_product_quantity(order_list, product_sku_id):
        """
        订单数量可能存在一模一样的两行，需要聚合数量，到数据库时则为一条数据
        PO-211-10119868847992801
        PO-211-12423433400871071
        PO-211-02796169632551140
        """
        total_quantity = 0
        # 有n个一模一样的productSkuId
        n = 0
        for order in order_list:
            if order['productInfoList'][0]['productSkuId'] == product_sku_id:
                n = n + 1
                total_quantity += order['productInfoList'][0]['productQuantity']
        return total_quantity, n-1

    def etl_order_list(self):
        """
        temu-跨境卖家中心-订单管理-订单列表-买家履约订单
        :return:处理好的、用于插入数据库的数据
        """
        j = 0
        data_list = []
        discount_list = []
        order_list, mongodb_count = self.get_mongodb_one_month(orderlist_table_name)
        logger.info(
            f'从mongo取出的最近30天的行数为 {mongodb_count} 行')
        for order in order_list:
            i = 0
            orderList = order['orderList']
            for data in orderList:
                i = i + 1  # 计算存在多个spu的订单数量
                productQuantity, count = self.sum_product_quantity(orderList, data['productInfoList'][0]['productSkuId'])
                new_data = {
                    'dt': order['dt'],
                    'parentOrderSn': order['parentOrderSn'],
                    'siteName': order['parentOrderMap']['siteName'],
                    'regionName1': order['parentOrderMap']['regionName1'],
                    'parentOrderStatus': order['parentOrderMap']['parentOrderStatus'],
                    'extCodeList': data['extCodeList'][0],
                    'productSkuId': data['productInfoList'][0]['productSkuId'],
                    'productSkcId': data['productInfoList'][0]['productSkcId'],
                    'productSpuId': data['productInfoList'][0]['productSpuId'],
                    'productQuantity': productQuantity,
                    'goodsName': data['goodsName'],
                    'orderSn': data['orderSn'],
                    'spec': data['spec'],
                    'warehouseName': data['warehouseName'],
                    'thumbUrl': data['thumbUrl'],
                    'shippedQuantity': data['shippedQuantity'],
                    'relatedGoodsInfoForAggregation': json.dumps(self.find_package_tracking_company(order, data['goodsId'])),
                    'parentOrderTimeStr': order['parentOrderMap']['parentOrderTimeStr'],
                    'parentOrderPendingEndTimeStr': order['parentOrderMap']['parentOrderPendingEndTimeStr'],
                    'expectShipLatestTimeStr': order['parentOrderMap']['expectShipLatestTimeStr'],
                    'parentShippingTimeStr': order['parentOrderMap']['parentShippingTimeStr'],
                    'expectDeliveryEndTimeStr': order['parentOrderMap']['expectDeliveryEndTimeStr'],
                    'parentReceiptTimeStr': order['parentOrderMap']['parentReceiptTimeStr'],
                    'mallName': order['mallName'],
                    'mallId': order['mallId'],
                }
                data_list.append(new_data)
                if i >1:
                    j = j + 1
                if count > 0:
                    discount_tup = (new_data['parentOrderSn'], productQuantity, new_data['mallName'], new_data['productSkuId'])
                    discount_list.append(discount_tup)
        logger.info(
            f'一个订单号会对应多个spu  会额外增加{j} 行')
        logger.info(
            f'聚合相同的子订单信息后  最终行数为 {len(data_list) - len(discount_list) + len(set(discount_list))} 行')
        return data_list

    def main(self):
        pass


if __name__ == "__main__":
    tb = MongoTidbTransferOrderList()
    tb.main()
