# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 品牌品类划分

from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("品牌品类划分  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("品牌品类划分  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-4IA668912Q8ECRDF9LU6H7E1S9S72P2A26KML1'
    i = Sync()
    i.main(form_uuid)
    '''
    {"brand": "品牌", "brand_category": "品牌+品类", "category": "品类"}
    '''