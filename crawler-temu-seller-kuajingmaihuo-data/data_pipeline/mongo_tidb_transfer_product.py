# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 10:52
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import json

from base.crawler_base import CrawlerBase
from settings import db_name, table_name


class MongoTidbTransfer(CrawlerBase):
    def __init__(self):
        super().__init__()
        # self.table_ob = self.mongo_ob.load_table_ob(db_name, table_name)

    @staticmethod
    def get_category_string(categories):
        """
        拼接成指定格式s>b>c
        :param categories:
        :return:str
        """
        # 使用列表推导式获取所有的 catName:
        # key.startswith('cat') ,如果键名以 'cat' 开始，这个表达式就会返回 True，否则返回 False。
        # value['catName'] 是在字典 value 中查找键为 'catName' 的值，如果该键存在且对应的值不为空
        # （在 Python 中，空字符串、0、None 和空的数据结构都被视为 False），这个表达式就会返回 True，否则返回 False。
        cat_names = [value['catName'] for key, value in categories.items() if
                     isinstance(value, dict) and key.startswith('cat') and value['catName']]

        # 使用 join 函数连接所有的 catName
        cat_names_string = ' > '.join(cat_names)

        return cat_names_string

    def etl_data(self):
        """
        temu-跨境卖家中心-商品管理-商品列表主要数据清洗
        :return:处理好的、用于插入数据库的数据
        """
        product_list = []
        data_list = self.get_mongodb_table(table_name)
        for data in data_list:
            new_data = {
                'productId': data['productId'],  # 'SPU ID'
                'productSkcId': data['productSkcId'],  # 'SKC ID'
                'productName': data['productName'],  # '商品名称'
                'extCode': data['extCode'],  # '货号'
                'catName': data['leafCat']['catName'],  # '类目'
                'leafCat': self.get_category_string(data['categories']),  # '类目结构'
                'mainImageUrl': data['mainImageUrl'],  # '图片'
                'siteName': data['productSemiManaged']['bindSites'][0]['siteName'],  # '经营站点'
                'productProperties': json.dumps(data['productProperties']),  # '商品属性'
                'sizeTemplateIds': data['sizeTemplateIds'],  # '尺码表
                'instructioninfo': None,  # '说明书信息'
                'createdAt': CrawlerBase().timestr(data['createdAt']),  # '创建时间'
            }
            product_list.append(new_data)
        return product_list

    def etl_Details_data(self):
        """
        temu-跨境卖家中心-商品管理-商品列表明细数据清洗
        :return:处理好的、用于插入数据库的数据
        """
        product_details_list = []
        data_list = self.get_mongodb_table(table_name)
        for data in data_list:
            productId = data['productId']
            productSkcId = data['productSkcId']
            warehouseRegion1List = data['productSemiManaged']['productShipment']['freightTemplate']['warehouseRegion1List']
            if warehouseRegion1List:
                chineseName = warehouseRegion1List[0]['chineseName']
            else:
                chineseName = None
            for item in data['productSkuSummaries']:
                new_data = {
                    'productId': productId,  # 'SPU ID'
                    'productSkcId': productSkcId,  # 'SKC ID'
                    'productSkuId': item['productSkuId'],  # 'SKU ID'
                    'productSkuSpecList': json.dumps(item['productSkuSpecList']),  # '商品规格'
                    'productSkuShippingMode': item['productSkuSaleExtAttr']['productSkuShippingMode'],
                    # '发货模式(1:卖家自发货,2：合作对接仓发货)'
                    'skuStockQuantity': item['productSkuSemiManagedStock']['skuStockQuantity'],  # '库存'
                    'existShippingShelfRoute': item['productSkuSemiManagedStock']['existShippingShelfRoute'],
                    # '是否展示库存标(true默认:展示)'
                    'chineseName': chineseName,  # '运费模版发货地'
                    'numberOfPieces': '单品数量：' + str(item['productSkuMultiPack']['numberOfPieces']) + '件',
                    # 'SKU分类(默认:单品数量：1件)'
                    'supplierPrice': item['siteSupplierPrices'][0]['supplierPrice'] / 100,  # '申报价格(CNY)'
                    'productSkuVolume': json.dumps(item['productSkuWhExtAttr']['productSkuVolume']),  # '体积
                    'productSkuWeight': json.dumps(item['productSkuWhExtAttr']['productSkuWeight']),  # '重量'
                    'extCode': item['extCode'],  # 'SKU货号'
                    'currencyType': item['currencyType'],  # 'currencyType'
                    'thumbUrl': item['thumbUrl'],  # 'thumbUrl'
                }
                product_details_list.append(new_data)
        return product_details_list

    def main(self):
        pass


if __name__ == "__main__":
    tb = MongoTidbTransfer()
    tb.main()
