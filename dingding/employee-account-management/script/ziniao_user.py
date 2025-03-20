# -*- coding: utf-8 -*-
# @Time     : 2024/11/25 16:03
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : ziniao_user.py
from loguru import logger
from crawler.ziniao import ZiniaoApi
from base import Base
from schema import GeneralResponseSchema


# 数据库表
DB_TABLE = 'dim_prod.dim_dsd_zn_staff_list_i_d'
FIELD_LIST = ['userid', 'username', 'fullname', 'mobile', 'auth_phone', 'level', 'status', ]



class ZiniaoUser(Base):
    def __init__(self):
        super().__init__()
        self.zn = ZiniaoApi()

    def get_user_list_to_tidb(self):
        """
        api: 获取紫鸟用户插入数据库
        # :param request: dict
        :return:
        """
        return_action = '获取紫鸟用户插入数据库'

        resp_gul = self.zn.get_user_list()  # 获取用户列表
        resp_id = self.tidb_ob.insert(DB_TABLE, FIELD_LIST, resp_gul['data'])  # 插入数据
        resp_gul['data'] = None  # 插入后清空用户列表数据
        return_data = [resp_gul, resp_id]  # 返回数据, 包含两个方法的执行情况

        return GeneralResponseSchema(action=return_action, data=return_data).to_dict()


    def set_user_status(self, uid, status):
        """
        api: 设置紫鸟用户状态
        :param uid:
        :param status:
        :return:
        """
        return_action = '设置紫鸟用户状态'
        return_result = ''

        query_sql = f'select * from {DB_TABLE} where userid={uid}'
        resp_qo = self.tidb_ob.query(query_sql, fetch='one')  # 查询用户信息
        if resp_qo['code'] != 0:
            return_result += f'查询用户信息失败, 请检查用户ID是否正确, userid: {uid}'
            return GeneralResponseSchema(action=return_action, result=return_result, data=resp_qo).to_dict()
        user = resp_qo['data']
        resp_du = self.zn.disable_user(uid, status, username=user['username'], fullname=user['fullname'])  # 禁用用户
        resp_qo['data'] = None
        return_data = [resp_qo, resp_du]  # 返回数据, 包含两个方法的执行情况

        return GeneralResponseSchema(action=return_action, data=return_data).to_dict()

    def main(self):
        logger.info('开始同步: 紫鸟用户信息')
        resp_gultt = self.get_user_list_to_tidb()

        logger.info('同步完成: 紫鸟用户信息')
        return resp_gultt

if __name__ == '__main__':
    obj = ZiniaoUser()

    print(obj.main())
    # print(obj.get_user_list_to_tidb())
    # print(obj.set_user_status(uid=16300804597736, status=0))
