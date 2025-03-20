# -*- coding: utf-8 -*-
# @Time     : 2024/11/26 11:33
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : jushuitan_user.py
from loguru import logger
from crawler.jushuitan import JushuitanCrawler
from base import Base
from schema import GeneralResponseSchema

# 数据库表
DB_TABLE = 'dim_prod.dim_dsd_jst_user_list_i_d'
FIELD_LIST = ['userid', 'username', 'iscompanyadmin', 'loginid', 'mobile', 'email', 'enabled', 'locked', 'remark',
              'created', 'modifiername', 'modified', 'pwdmodified', 'lastlogintime', ]


class JushuitanUser(Base):
    def __init__(self):
        super().__init__()

        self.jst = JushuitanCrawler()

    def get_user_list_to_tidb(self):
        """
        获取聚水潭用户信息
        :param request:
        :return:
        """
        return_action = '获取聚水潭用户列表存入数据库'
        resp_gul = self.jst.get_user_list()
        resp_i = self.jst.tidb_ob.insert(DB_TABLE, FIELD_LIST, resp_gul['data'])  # 插入数据
        resp_gul['data'] = None  # 插入后清空用户列表数据
        return_data = [resp_gul, resp_i]  # 返回数据, 包含两个方法的执行情况

        return GeneralResponseSchema(action=return_action, data=return_data).to_dict()

    def set_user_status(self, uid, status):
        """
        禁用/启用用户
        :param request:
        :return:
        """
        return_action = '设置聚水潭用户状态'

        resp_du = self.jst.deactivate_user(uid, status)

        return GeneralResponseSchema(action=return_action, data=[resp_du]).to_dict()

    def main(self):
        logger.info('开始同步: 聚水潭用户信息')
        resp_gultt = self.get_user_list_to_tidb()

        logger.info('同步完成: 聚水潭用户信息')
        return resp_gultt

if __name__ == '__main__':
    obj = JushuitanUser()

    print(obj.main())
    # print(obj.get_user_list_to_tidb())
    # print(obj.set_user_status(12279704, 0))
