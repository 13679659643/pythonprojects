# _*_ coding: utf-8 _*_
# @Time : 2024-12-13
# @Author : 李仕春
# @Email ： scli@doocn.com
# @File : common-yida-data-to-tidb
# @Desc : 海外仓接收货件地址数据
from loguru import logger

from common import BaseSync


class Sync(BaseSync):
    def main(self, form_uuid):
        """
        启动程序
        """
        logger.info("材料价格跟踪数据  表正在更新数据！")
        self.sync(form_uuid)
        logger.info("材料价格跟踪数据  表数据更新完成！")



if __name__ == '__main__':
    sync_obj = Sync()
    form_uuid = "FORM-E2AC0CD333B14A6493DDE57D162729C58PLV"
    sync_obj.main(form_uuid)

"""  
{"warehouse_name":"仓库名称",
    "recipient":"收货人",
    "phone_number":"电话",
    "address":"地址",
    "city":"城市",
    "state_province":"省份/州",
    "state_province_code":"省份/州代码",
    "country":"国家",
    "country_code":"国家代码",
    "postal_code":"邮政编码"}
"""