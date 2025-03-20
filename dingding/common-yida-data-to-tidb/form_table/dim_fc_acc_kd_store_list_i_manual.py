# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 金蝶账单明细-店铺配置表


from loguru import logger

from common import BaseSync


class Sync(BaseSync):


    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("金蝶账单明细-店铺配置表  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("金蝶账单明细-店铺配置表  表数据更新完成！")


if __name__ == '__main__':
    form_uuid = 'FORM-AC666081GGMCCTCNEWGMI6YVPGRU2HJO4GAKL1'
    i = Sync()
    i.main(form_uuid)
    '''
    {"id": "id", "inner_account_id": "inner_account_id", "kingdee_bank_account": "kingdee_bank_account",
     "kingdee_customer_number": "kingdee_customer_number", "kingdee_department_name": "kingdee_department_name",
     "kingdee_department_number": "kingdee_department_number", "kingdee_org": "kingdee_org",
     "kingdee_settlement_mode": "kingdee_settlement_mode", "platform_account": "platform_account",
     "sale_department_number": "sale_department_number", "shop_name": "shop_name"}
    '''
