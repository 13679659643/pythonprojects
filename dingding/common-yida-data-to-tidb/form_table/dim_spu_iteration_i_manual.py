# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 货号颜色迭代表

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
    form_uuid = 'FORM-2J6666D16H0E47Q6B9DM46D5G24K3W6W2X9ML8'
    i = Sync()
    i.main(form_uuid)
    '''
    {"iterated_color": "迭代颜色", "iterated_spu": "迭代SPU", "iterated_style": "迭代款号",
     "iterated_style_color": "迭代款号颜色", "latest_color": "最新颜色", "latest_spu": "最新SPU",
     "latest_style_code": "当前使用货号", "original_color": "原颜色", "original_spu": "原SPU",
     "original_style_code": "原货号", "upgrade_content": "升级内容"}
    '''

