# -*- coding: utf-8 -*-
# @Time     : 2024/11/26 15:41
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : synology_user.py
from loguru import logger
from crawler.synology import SynologyApi
from base import Base
from schema import GeneralResponseSchema

# 数据库表
DB_TABLE = 'dim_prod.dim_dsd_synology_user_list_i_d'
FIELD_LIST = ['uid', 'region', 'name', 'email', 'description', 'expired']
# 群晖配置

SYNOLOGY_CONFIG = {
    'chengdu': {
        'host': 'nas5.doocn.com',
        'port': 7000,
        'ssh_ip': '192.168.0.10',
        'ssh_port': 32522,
        'username': 'nas',
        'password': 'Doocn2024000'
    },
    'quanzhou': {
        'host': 'nas3.doocn.com',
        'port': 7000,
        'ssh_ip': '110.81.198.238',
        'ssh_port': 52322,
        'username': 'nas',
        'password': 'Doocn2024000'
    }
}


class SynologyUser(Base):
    def __init__(self):
        super().__init__()

    def get_user_list_to_tidb(self):
        """
        api: 获取群晖用户列表插入数据库

        :return:
        """
        return_action = '获取群晖用户列表插入数据库'
        return_data = []

        user_list = []
        tidb_ob = None
        for region, config in SYNOLOGY_CONFIG.items():
            with SynologyApi(**config) as syno:  # 初始化

                resp_gul = syno.get_user_list()  # 获取用户列表
                if resp_gul['code'] == 0:
                    for item in resp_gul['data']:
                        item['region'] = region
                        user_list.append(item)

                resp_gul['data'] = region
                return_data.append(resp_gul)

                tidb_ob = syno.tidb_ob

        resp_id = tidb_ob.insert(DB_TABLE, FIELD_LIST, user_list)  # 插入数据
        return_data.append(resp_id)

        return GeneralResponseSchema(action=return_action, data=return_data).to_dict()

    def set_user_status(self, region, username, status):
        """
        禁用/启用用户
        :param region: 地区
        :param username: 用户名
        :param status: 状态 1启用 0禁用

        :return:
        """
        return_action = '设置群晖用户状态'

        with SynologyApi(**SYNOLOGY_CONFIG[region]) as syno:
            return_data = syno.modify_user(username, status)

            return GeneralResponseSchema(action=return_action, data=[return_data]).to_dict()

    def main(self):
        logger.info('开始同步: 群晖用户信息')
        resp_gultt = self.get_user_list_to_tidb()

        logger.info('同步完成: 群晖用户信息')
        return resp_gultt

if __name__ == '__main__':
    obj = SynologyUser()
    print(obj.set_user_status('chengdu', 'DOOCN-高逸晖', 0))
    print(obj.main())
