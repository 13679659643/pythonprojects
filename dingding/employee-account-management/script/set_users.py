# -*- coding: utf-8 -*-
# @Time     : 2024/12/20 10:02
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : set_users.py

from base import Base
from script.ziniao_user import ZiniaoUser
from script.synology_user import SynologyUser
from script.lingxing_user import LingxingUser
from script.jushuitan_user import JushuitanUser
from config.query_sql import query_sql_resignation_users


class SetUsers(Base):
    def __init__(self, name: str = None, status: int = 0):
        super().__init__()
        self.name = name
        self.status = status

    def get_users_waiting_to_be_setup(self):
        """
        获取等待设置的用户
        :return:
        """
        query_resp = self.tidb_ob.query(query_sql_resignation_users(self.name))
        return query_resp['data']

    def set_user_status(self, user: dict):
        """
        设置用户状态
        :param user: 用户信息
        :param status: 状态: 1 启用, 0 停用
        :return:
        """
        platform = user['platform']
        params = {
            'uid': user['uid'],
            'status': self.status
        }
        ob = None
        if platform == 'lingxing':
            ob = LingxingUser()
        if platform == 'jushuitan':
            ob = JushuitanUser()
        if platform == 'synology':
            ob = SynologyUser()
            del params['uid']
            params['username'] = user['username']
            params['region'] = user['region']
        if platform == 'ziniao':
            ob = ZiniaoUser()

        if ob:
            resp1 = ob.set_user_status(**params)
            resp2 = ob.get_user_list_to_tidb()

            return [resp1, resp2]

    def main(self):
        """
        入口函数
        默认获取离职的用户
        :return:
        """
        users = self.get_users_waiting_to_be_setup()
        return [self.set_user_status(user) for user in users]



if __name__ == '__main__':
    obj = SetUsers('刘云飞', 1)
    print(obj.main())
