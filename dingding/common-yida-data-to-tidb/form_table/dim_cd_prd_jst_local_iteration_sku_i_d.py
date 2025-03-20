# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : local_sku迭代

from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("local_sku迭代  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("local_sku迭代  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-0A966I81QD2EMY05CPFV6ABPBO8P3T8ZT9AMLA'
    i = Sync()
    i.main(form_uuid)
    '''
    {"iteration_sku": "迭代sku", "local_sku": "local_sku"}
    '''