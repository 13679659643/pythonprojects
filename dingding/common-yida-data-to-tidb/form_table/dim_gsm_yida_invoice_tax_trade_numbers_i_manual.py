# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 11:29
# @Author  : Night
# @File    : dim_gsm_yida_invoice_tax_trade_numbers_i_manual.py
# @Description:
from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("DS-发票-海关识别号  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("DS-发票-海关识别号  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-7C74ED8937FB43BC93251A113D46AB1BPME7'
    i = Sync()
    i.main(form_uuid)
    '''
    {"store":"店铺","vat":"VAT","eori":"EORI"}
    '''
