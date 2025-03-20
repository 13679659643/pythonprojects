# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 11:31
# @Author  : Night
# @File    : dim_gsm_yida_invoice_sale_link_i_manual.py
# @Description:
from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("DS-发票-销售链接  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("DS-发票-销售链接  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-9D6A7EC84DFB4A5496219A450FCD2CFAEURV'
    i = Sync()
    i.main(form_uuid)
    '''
    {"brand":"品牌","store":"店铺","sale_link":"销售链接"}
    '''