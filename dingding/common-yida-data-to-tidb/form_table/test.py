# -*- coding: utf-8 -*-
# @Time    : 2025/2/14 15:58
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:

from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("货号颜色迭代表  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("货号颜色迭代表  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-A4FE876D1DBB47FEB7F11583238F553364K1'
    i = Sync()
    i.main(form_uuid)
    '''
    {"iterated_color": "迭代颜色", "iterated_spu": "迭代SPU", "iterated_style": "迭代款号",
     "iterated_style_color": "迭代款号颜色", "latest_color": "最新颜色", "latest_spu": "最新SPU",
     "latest_style_code": "当前使用货号", "original_color": "原颜色", "original_spu": "原SPU",
     "original_style_code": "原货号", "upgrade_content": "升级内容"}
    '''

