# -*- coding: utf-8 -*-
# @Time     : 2025/1/25 13:52
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : tidb_insert_lingxing_data.py
# Tidb插入领星数据
import json
import logging
import time
import traceback
from typing import List, Any

from loguru import logger

from base import Base
from common import Utils
from crawler import LingxingCrawler
from schema import general_response_decorator, GeneralResponseSchema
from settings.db_model import *
from script.lingxing.tidb_query_lingxing_data import TidbQueryLingxingData


class TidbInsertLingxingData(Base):
    def __init__(self):
        super().__init__()
        self.lingxing_crawler = LingxingCrawler()
        self.tidb_query_lingxing = TidbQueryLingxingData()

    @general_response_decorator(description='插入领星用户列表', is_message=True)
    def insert_user_list(self):
        resp = self.lingxing_crawler.get_user_list()  # 获取数据
        data_list = [Utils.replace_dict_key(item, RULES_USER_LIST) for item in resp.data]  # 替换字段名
        self.tidb_ob.commit(CREATE_TABLE_USER_LIST)  # 创建表
        self.tidb_ob.commit(TRUNCATE_TABLE_USER_LIST)  # 清空表
        insert_resp = self.tidb_ob.insert(DB_TABLE_USER_LIST, FIELD_LIST_USER_LIST, data_list)  # 插入数据
        logger.info(insert_resp)

        return insert_resp.message

    @general_response_decorator(description='插入领星用户详情', is_message=True)
    def insert_user_info(self):
        user_list = self.tidb_query_lingxing.get_user_list()  # 获取用户列表
        data_list = []

        for user in user_list:
            resp = self.lingxing_crawler.get_user_info(user['uid'])  # 获取用户详情
            data = Utils.replace_dict_key(resp.data, RULES_USER_INFO)
            data['alibaba_id'] = json.dumps(data['alibaba_id'])
            data['email_relation_id'] = json.dumps(data['email_relation_id'])
            data['group_id'] = json.dumps(data['group_id'])
            data['org_sids'] = json.dumps(data['org_sids'])
            data['sid'] = json.dumps(data['sid'])
            data['transparent_account_ids'] = json.dumps(data['transparent_account_ids'])
            data['user_org_dtos'] = json.dumps(data['user_org_dtos'])
            data['warehouse_id'] = json.dumps(data['warehouse_id'])
            data_list.append(data)

        self.tidb_ob.commit(CREATE_TABLE_USER_INFO)  # 创建表
        # self.tidb_ob.commit(TRUNCATE_TABLE_USER_INFO)  # 清空表
        insert_resp = self.tidb_ob.insert(DB_TABLE_USER_INFO, FIELD_LIST_USER_INFO, data_list)  # 插入数据
        logger.info(insert_resp)

        return insert_resp.message

    @general_response_decorator(description='插入领星用户店铺映射表', is_message=True)
    def insert_user_mapping_store(self):
        sql = """
        select dlulih.uid,
               dluilih.sid
        from dim_prod.dim_lx_user_list_i_h dlulih
                 left join dim_prod.dim_lx_user_info_list_i_h dluilih
                           on dlulih.uid = dluilih.uid
        """
        query_resp = self.tidb_ob.query(sql)
        data_list = []
        for item in query_resp.data:
            uid = item['uid']
            for sid in json.loads(item['sid']):
                data_list.append(dict(uid=uid, sid=sid))
        insert_resp = self.tidb_ob.insert('dim_prod.dim_lx_user_mapping_store_i_h', ['uid', 'sid'], data_list)
        logger.info(insert_resp)

        return insert_resp.message

    @general_response_decorator(description='插入领星角色数据', is_message=True)
    def insert_role_data(self):
        resp = self.lingxing_crawler.get_role_list()  # 获取数据
        data_list = [Utils.replace_dict_key(item, RULES_ROLE_LIST) for item in resp.data]  # 替换字段名
        self.tidb_ob.commit(CREATE_TABLE_ROLE_LIST)  # 创建表
        self.tidb_ob.commit(TRUNCATE_TABLE_ROLE_LIST)  # 清空表
        insert_resp = self.tidb_ob.insert(DB_TABLE_ROLE_LIST, FIELD_LIST_ROLE_LIST, data_list)  # 插入数据
        logger.info(insert_resp)

        return insert_resp.message

    @general_response_decorator(description='从数据库获取lx角色id')
    def get_role_id(self) -> list[Any]:
        sql = f"""
        select id
        from {DB_TABLE_ROLE_LIST}
        """
        query_resp = self.tidb_ob.query(sql)
        id_list = []
        for item in query_resp.data:
            id = item['id']
            id_list.append(id)
        return id_list

    @general_response_decorator(description='插入领星角色用户数据', is_message=True)
    def insert_role_user_data(self):
        id_list = self.get_role_id()
        self.tidb_ob.commit(CREATE_TABLE_ROLE_USER_LIST)
        self.tidb_ob.commit(TRUNCATE_TABLE_ROLE_USER_LIST)
        insert_list = []
        for id in id_list.data:
            resp = self.lingxing_crawler.get_role_user_list(id)
            data_list = [Utils.replace_dict_key({**item, 'id': id}, RULES_ROLE_USER_LIST) for item in resp.data]
            insert_list.extend(data_list)
        insert_resp = self.tidb_ob.insert(DB_TABLE_ROLE_USER_LIST, FIELD_LIST_ROLE_USER_LIST, insert_list)
        logger.info(insert_resp)

        return insert_resp.message

    @general_response_decorator(description='插入领星功能\字段权限数据', is_message=True)
    def insert_role_action_perm(self):
        id_list = self.get_role_id()
        self.tidb_ob.commit(CREATE_TABLE_ACTION_PERM_LIST)
        self.tidb_ob.commit(TRUNCATE_TABLE_ACTION_PERM_LIST)
        insert_list = []
        for id in id_list.data:
            try:
                resp = self.lingxing_crawler.get_role_action_perm(id)
                data_list = resp.data['func_perms']
                insert_list.extend(data_list)
            except TypeError:
                print(f"Error occurred with id: {id}")
                continue
        insert_resp = self.tidb_ob.insert(DB_TABLE_ACTION_PERM_LIST, FIELD_LIST_ACTION_PERM_LIST, insert_list)
        logger.info(insert_resp)

        return insert_resp.message

    # 插入数据权限
    @general_response_decorator(description='插入领星角色数据权限', is_message=1)
    def insert_role_data_perms(self):
        id_list = self.get_role_id()
        self.tidb_ob.commit(CREATE_TABLE_DATA_PERM_LIST)
        self.tidb_ob.commit(TRUNCATE_TABLE_DATA_PERM_LIST)
        insert_list = []
        for id in id_list.data:
            try:
                resp = self.lingxing_crawler.get_role_data_perm(id)
                data_list = resp.data
                insert_list.extend(data_list)
            except TypeError:
                print(f"Error occurred with id: {id}")
                continue
        insert_resp = self.tidb_ob.insert(DB_TABLE_DATA_PERM_LIST, FIELD_LIST_DATA_PERM_LIST, insert_list)
        logger.info(insert_resp)

        return insert_resp.message


if __name__ == '__main__':
    instance = TidbInsertLingxingData()


    instance.insert_user_list()
    instance.insert_user_info()


    instance.insert_role_data()
    time.sleep(1)
    instance.insert_role_user_data()
    time.sleep(1)
    start_time = time.time()
    instance.insert_role_action_perm()
    time.sleep(1)
    end_time = time.time()
    time_diff = round((end_time - start_time), 2)
    logger.info(f"时间间隔：{time_diff} 秒")
    start_time1 = time.time()
    instance.insert_role_data_perms()
    time.sleep(1)
    end_time1 = time.time()
    time_diff = round((end_time1 - start_time1), 2)
    logger.info(f"时间间隔：{time_diff} 秒")
