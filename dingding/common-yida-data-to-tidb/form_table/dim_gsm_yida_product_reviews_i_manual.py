# _*_ coding: utf-8 _*_
# @Time : 2024/6/18
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : DS-Listing评价监控-管理


from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("DS-Listing评价监控-管理  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("DS-Listing评价监控-管理  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-D9B2431B6517411A8FE065BF79BC3F97GKW5'
    i = Sync()
    i.main(form_uuid)
    '''
    {"store_name":"店铺","msku":"msku","asin":"asin","site":"站点"}
    '''