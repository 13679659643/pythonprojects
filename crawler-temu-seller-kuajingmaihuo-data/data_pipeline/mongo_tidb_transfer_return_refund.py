# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 10:52
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import json

from loguru import logger

from base.crawler_base import CrawlerBase
from settings import return_refund_table_name


class MongoTidbTransferReturnRefund(CrawlerBase):
    """temu-跨境卖家中心-订单管理-订单列表-退货退款"""

    def __init__(self):
        super().__init__()

    def etl_return_refund_list(self):
        """
        temu-跨境卖家中心-订单管理-订单列表-退货退款
        :return:处理好的、用于插入数据库的数据
        """
        data_list = []
        return_refund_list, mongodb_count = self.get_mongodb_one_month(return_refund_table_name)
        logger.info(
            f'从mongo取出的最近61天的行数为 {mongodb_count} 行')
        i = 0
        for item in return_refund_list:
            afterSalesItemVOList = item['afterSalesItemVOList']
            # 由于一个订单可能会出现多双退货，所以在此统计会增加的行数
            i = i+len(afterSalesItemVOList)-1
            for goods in afterSalesItemVOList:
                new_data = {
                    'dt': item['dt'],  # 售后时间
                    'parentAfterSalesSn': item['parentAfterSalesSn'],  # 售后单号
                    'afterSalesTypeDesc': item['afterSalesTypeDesc'],  # 售后单类型
                    'afterSalesTypeRemark': item['afterSalesTypeRemark'],  # 售后单类型备注描述
                    'goodsName': goods.get('goodsName'),  # 标题
                    'goodsSpec': goods.get('goodsSpec'),  # 属性
                    'productSkuId': goods.get('productSkuId'),  # 货号颜色尺码,SKU是对可以独立管理、独立核算、独立销售的最小单位进行编码的结果。
                    'productSkcId': goods.get('productSkcId'),  # SKC是对同一款式、不同颜色的商品的统称
                    'productSpuId': goods.get('productSpuId'),  # SPU是指同一款式，不考虑颜色、尺寸等差异的商品的统称。
                    'afterSalesSn': goods.get('afterSalesSn'),  # 售后子单号
                    'goodsThumbUrl': goods.get('goodsThumbUrl'),  # 鞋子图片
                    'regionName1': item['regionName1'],  # 国家地区
                    'afterSalesReasonDesc': goods.get('afterSalesReasonDesc'),  # 退货或退款原因
                    'buyerComment': goods.get('buyerComment'),  # 用户退货或退款翻译后描述
                    'originalBuyerComment': goods.get('originalBuyerComment'),  # 用户退货或退款翻译后描述原文
                    'parentOrderSn': item['parentOrderSn'],  # 子订单号
                    'parentOrderShippingStatusDesc': item['parentOrderShippingStatusDesc'],  # 订单状态
                    'applicantScene': item['applicantScene'],  # 售后来源
                    'operateNodeVOList': json.dumps(item['operateNodeVOList']),  # 操作节点:列表内各类时间，顺序不定，列表长度不定，固使用json格式直接存储
                    'returnLogisticList': json.dumps(item['returnLogisticList']),  # 退货运单信息
                    'returnWareHouse': item['returnWareHouse'],  # 退回目的地
                    'pickUpParentTypeDesc': item['pickUpParentTypeDesc'],  # 是否通过平台下单退货物流
                    'parentAfterSalesStatusDesc': item['parentAfterSalesStatusDesc'],  # 售后状态
                    'mallName': item['mallName'],  # 店铺名称
                    'mallId': item['mallId'],  # 店铺id
                    'domain_url': item['domain_url'],  # 域名
                }
                data_list.append(new_data)
        logger.info(f'由于一个订单可能会出现多双退货，所以在此统计会增加的行数: {i} 行！')
        return data_list

    def main(self):
        pass


if __name__ == "__main__":
    tb = MongoTidbTransferReturnRefund()
    tb.main()
