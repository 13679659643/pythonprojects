# -*- coding: utf-8 -*-
# @Time     : 2024/11/25 17:51
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : lingxing_user.py
from loguru import logger
from crawler.lingxing import LingxingCrawler
from base import Base
from schema import GeneralResponseSchema

# 数据库表
DB_TABLE = 'dim_prod.dim_dsd_lx_user_list_i_d'
FIELD_LIST = ['uid', 'username', 'mobile', 'email', 'realname', 'role', 'create_time', 'last_login_time',
              'last_login_ip', 'status', ]


class LingxingUser(Base):
    def __init__(self):
        super().__init__()
        self.lx = LingxingCrawler()

    def get_user_list_to_tidb(self):
        """
        获取中鸟用户信息
        :param request:
        :return:
        """
        return_action = '获取领星用户列表存入数据库'

        resp_gul = self.lx.get_user_list()
        resp_i = self.tidb_ob.insert(DB_TABLE, FIELD_LIST, resp_gul['data'])  # 插入数据
        resp_gul['data'] = None  # 插入后清空用户列表数据
        return_data = [resp_gul, resp_i]  # 返回数据, 包含两个方法的执行情况

        return GeneralResponseSchema(action=return_action, data=return_data).to_dict()

    def set_user_status(self, uid, status):
        """
        禁用/启用用户
        :param request:
        :return:
        """
        return_action = '设置领星用户状态'
        resp_du = self.lx.deactivate_user(uid, status)

        return GeneralResponseSchema(action=return_action, data=[resp_du]).to_dict()

    def main(self):
        logger.info('开始同步: 领星用户信息')
        resp_gultt = self.get_user_list_to_tidb()

        logger.info('同步完成: 领星用户信息')
        return resp_gultt

if __name__ == '__main__':
    obj = LingxingUser()

    print(obj.main())
    # print(obj.get_user_list_to_tidb())
    # print(obj.set_user_status(10375154, 0))
