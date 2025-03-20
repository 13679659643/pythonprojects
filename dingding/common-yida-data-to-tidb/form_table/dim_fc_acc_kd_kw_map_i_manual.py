# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 金蝶账单明细-费用项目关键字映射

from loguru import logger

from common import BaseSync


class Sync(BaseSync):

    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("金蝶账单明细-费用项目关键字映射  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("金蝶账单明细-费用项目关键字映射  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-PR8667D1ZEFCSP57EQGL695T8SXJ2QIBKZ1KLA'
    i = Sync()
    i.main(form_uuid)
    '''
    {"id": "id", "key_word": "key_word", "kingdee_expense_name": "kingdee_expense_name",
     "kingdee_expense_number": "kingdee_expense_number"}
    '''
