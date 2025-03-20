# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 11:07
# @Author  : Night
# @File    : dim_gsm_yida_invoice_amz_tracking_code_i_manual.py
# @Description:
from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("DS-发票-亚马逊追踪编码  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("DS-发票-亚马逊追踪编码  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-6072FE4D332040EF8DD6A6A8439B15D2DXPO'
    i = Sync()
    i.main(form_uuid)
    '''
    {"shipment_id":"FBA发货单号","amazon_tracking_code":"亚马逊追踪编码"}
    '''