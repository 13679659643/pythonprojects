# -*- coding: utf-8 -*-
# @Time     : 2024/12/23 14:11
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : my_customize_tidb.py
import time
import traceback
from digiCore.db.tidb.core import TiDBDao
from digiCore.db.tidb.util import list_to_sql_values, create_insert_sql

from schema import GeneralResponseSchema


class MyTiDBDao(TiDBDao):
    """
    重写TiDBDao
    """
    def insert(self, db_table: str, field_list: list, data_list: [dict], max_retries=3,
               delay=1) -> GeneralResponseSchema:
        """
        插入数据到TiDB
        :param db_table: 数据库及表名称
        :param data_list: 字段对应的列表套字典数据
        :param field_list: 字段列表
        :param max_retries: 最大重试次数
        :param delay: 重试间隔时间（秒）
        :return: 操作结果
        """
        code = 0
        description = '数据插入TiDB'
        message = f'DB_TABLE: {db_table} '
        if not data_list:
            message += '数据为空，无需插入！'
            return GeneralResponseSchema(code=code, description=description, message=message)
        for attempt in range(max_retries):
            try:
                sql_values = list_to_sql_values(field_list, data_list)
                insert_sql = create_insert_sql(db_table, field_list, sql_values)
                with self.conn_pool as cursor:
                    cursor.execute(insert_sql)
                message += f'\n\t插入 {len(data_list)} 条'
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    code = 9
                    message += f'\n\t{str(e)}'
                    break
        return GeneralResponseSchema(code=code, description=description, message=message)

    def query(self, sql: str, fetch='all', max_retries=3, delay=1) -> GeneralResponseSchema:
        """
        查询并返回数据库中的一条数据
        :param sql: 查询sql语句
        :param fetch: fetch参数
        :param max_retries: 最大重试次数
        :param delay: 重试间隔时间（秒）
        :return: 操作结果
        """
        code = 0
        description = f'数据查询TiDB-fetch{fetch}'
        message = ''
        data = None
        fetch = fetch.lower()
        if fetch not in ['all', 'one']:
            code = 9
            message += '\n\tfetch参数错误，请输入all或one'
            return GeneralResponseSchema(code=code, description=description, message=message)
        for attempt in range(max_retries):
            try:
                with self.conn_pool as cursor:
                    cursor.execute(sql)
                    if fetch == 'all':
                        data = cursor.fetchall()
                        break
                    elif fetch == 'one':
                        data = cursor.fetchone()
                        break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    code = 1
                    message += f'\n\t{str(e)}'
                    break
        return GeneralResponseSchema(code=code, description=description, message=message, data=data)

    def commit(self, sql: str, max_retries=3, delay=1) -> GeneralResponseSchema:
        """
        查询并返回数据库中的一条数据
        :param sql: 查询sql语句
        :param max_retries: 最大重试次数
        :param delay: 重试间隔时间（秒）
        :return: 操作结果
        """
        code = 0
        description = f'提交SQL'
        message = ''
        data = None
        for attempt in range(max_retries):
            try:
                with self.conn_pool as cursor:
                    cursor.execute(sql)
                    if 'select' in sql.lower():
                        data = cursor.fetchall()
                    break
            except Exception as e:
                traceback.print_exc()
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    code = 9
                    message += f'\n\t{str(e)}'
                    break

        return GeneralResponseSchema(code=code, description=description, message=message, data=data)
