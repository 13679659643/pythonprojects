# -*- coding: utf-8 -*-
# @Time    : 2024/9/25 16:25
# @Author  : Night
# @File    : dim_gsm_yida_product_customs_code_i_manual.py
# @Description:
from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("DS-发票-国外海关编码  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("DS-发票-国外海关编码  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-AC19FC76BE5B4D389471FB299A6F8A7BGKNJ'
    i = Sync()
    i.main(form_uuid)
    '''
    {"original_spu":"货号","customs_code":"报关编码"}
    '''
