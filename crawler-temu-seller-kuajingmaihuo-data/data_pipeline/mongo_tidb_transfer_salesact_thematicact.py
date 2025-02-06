# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 10:52
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import json

from base.crawler_base import CrawlerBase
from settings import thematicact_table_name


class MongoTidbTransferShort(CrawlerBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def extract_fields(data):
        # 创建一个新的列表来保存提取的数据
        extracted_data = []
        for item in data:
            if 'extCode' in item and 'sitePriceList' in item and 'properties' in item:
                for site in item['sitePriceList']:
                    if 'siteName' in site:
                        extracted_data.append({
                            'extCode': item['extCode'],
                            'siteName': site['siteName'],
                            '颜色': item['properties']['颜色'],
                            '尺码': item['properties']['尺码']
                        })

        # 返回提取的数据
        return extracted_data

    @staticmethod
    def is_assignSessionList(assignSessionList: list, key: str):
        if assignSessionList:
            item = key
            return assignSessionList[0][item]
        else:
            return None

    @staticmethod
    def find_min_max_price(data):
        prices = []

        for item in data:
            # 如果 'sitePriceList' 在字典中，就遍历它
            if 'sitePriceList' in item:
                for site in item['sitePriceList']:
                    # 如果 'activityPrice' 在字典中并且不是 None，就添加到 prices 列表中
                    if 'activityPrice' in site and site['activityPrice'] is not None:
                        activityPrice = site['activityPrice']/100
                        prices.append(activityPrice)

        # 计算最大值和最小值
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None

        return min_price, max_price

    def etl_data(self):
        """
        temu-跨境卖家中心-店铺营销-营销活动-专题活动
        :return:处理好的、用于插入数据库的数据
        """
        thematicact_list = []
        data_list = self.get_mongodb_table(thematicact_table_name)
        for data in data_list:
            c = CrawlerBase()
            signUpTime = c.timestr(data['signUpTime'])
            new_data = {
                'dt': c.date_str(signUpTime),                                                                           # '提交日期'
                'id': data['id'],                                                                                       # 'id'
                'name': data['name'],                                                                                   # '商品信息_名称'
                'productId': data['productId'],                                                                         # 'SPU ID'
                'siteName': data['semiManagedBindSites'][0]['siteName'],                                                # '商品信息_经营站点'
                'pictureUrl': data['pictureUrl'],                                                                       # '商品信息_图片'
                'skcId': data['skcList'][0]['skcId'],                                                                   # 'SKC信息'
                'extCode': data['skcList'][0]['extCode'],                                                               # 'spu'
                'skuattributeset': json.dumps(self.extract_fields(data['skcList'][0]['skuList'])),                      # 'SKU属性集'
                'dailyPrice': data['skcList'][0]['skuList'][0]['sitePriceList'][0]['dailyPrice'] / 100,                 # '日常申报价'
                'activityPricemin': self.find_min_max_price(data['skcList'][0]['skuList'])[0],                          # '活动申报价最低'
                'activityPricemax': self.find_min_max_price(data['skcList'][0]['skuList'])[1],                          # '活动申报价最大'
                'targetActivityPrice': data['skcList'][0]['skuList'][0]['sitePriceList'][0]['targetActivityPrice'],     # '参考申报价(专题活动)'
                'currency': data['skcList'][0]['skuList'][0]['currency'],                                               # '币种'
                'signUpTime': data['signUpTime'],                                                                               # '提交时间'
                'invitationTypeName': data['invitationTypeName'],                                                       # '活动类型名称'
                'activityName': data['activityName'],                                                                   # '活动主题名称'
                'sessionName': self.is_assignSessionList(data['assignSessionList'], 'sessionName'),                     # '报名结果'
                'startDateStr': self.is_assignSessionList(data['assignSessionList'], 'startDateStr'),                   # '报名结果_开始时间'
                'endDateStr': self.is_assignSessionList(data['assignSessionList'], 'endDateStr'),                       # '报名结果_结束时间'
                'durationDays': self.is_assignSessionList(data['assignSessionList'], 'durationDays'),                   # '报名结果_间隔天数'
                'sessionStatus': self.is_assignSessionList(data['assignSessionList'], 'sessionStatus'),                  # '报名结果_状态(4:报名失败,3:活动已结束,2:进行中)'
                'activityStock': data['activityStock'],                                                                 # '场次共用活动库存_提报'
                'activityRemainStock': data['activityRemainStock'],                                                     # '场次共用活动库存_剩余'
                'suggestActivityStock': data['suggestActivityStock'],                                                   # 'suggestActivityStock'
                'mallName': data['mallName'],                                                                           # '店铺名称'
                'mallId': data['mallId'],                                                                               # 'mallId'
            }

            thematicact_list.append(new_data)
        return thematicact_list

    def main(self):
        pass


if __name__ == "__main__":
    tb = MongoTidbTransferShort()
    tb.main()
