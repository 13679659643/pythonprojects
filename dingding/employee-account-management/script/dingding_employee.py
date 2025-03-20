# -*- coding: utf-8 -*-
# @Time     : 2024/11/25 14:26
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : dingding_employee.py
import traceback
from loguru import logger
from crawler.dingding import DingdingApi
from base import Base
from schema import GeneralResponseSchema


# 数据库表
DEPARTMENT_DB_TABLE = 'dim_prod.dim_dsd_yida_dd_dept_a_d'
DEPARTMENT_FIELD_LIST = ['dept_id', 'parent_id', 'name']
EMPLOYEE_DB_TABLE = 'dim_prod.dim_dsd_yida_dd_employee_a_d'
EMPLOYEE_FIELD_LIST = ['userid', 'name', 'mobile', 'email', 'location', 'position', 'dept_id', 'dept_name',
                       'main_dept_id', 'main_dept_name', 'report_to']


class DingdingEmployee(Base):
    def __init__(self):
        super().__init__()
        self.dd = DingdingApi()

    def get_department_list_to_tidb(self):
        action = '获取部门列表插入数据库'

        resp_gdl = self.dd.get_department_list()  # 获取部门列表
        resp_c = self.tidb_ob.commit(f'truncate table {DEPARTMENT_DB_TABLE}')  # 清空表
        resp_i = self.tidb_ob.insert(DEPARTMENT_DB_TABLE, DEPARTMENT_FIELD_LIST, resp_gdl['data'])  # 插入数据
        resp_gdl['data'] = None  # 清空数据

        return GeneralResponseSchema(action=action, data=[resp_gdl, resp_c, resp_i]).to_dict()

    def get_department_employee_list_to_tidb(self):
        return_action = '获取部门员工列表插入数据库'

        resp_gdl = self.dd.get_department_list()  # 获取部门列表
        employee_list = []
        for dept in resp_gdl['data']:

            try:
                resp_gdel = self.dd.get_department_employee_list(dept['dept_id'])  # 获取部门员工列表
            except Exception as e:
                traceback.print_exc()
                return 1
            for employee in resp_gdel['data']:
                employee_info = {'userid': employee['userid']}

                resp_gri = self.dd.get_roster_information(employee['userid'])
                employee_info.update(resp_gri['data'])  # 获取员工详细信息
                employee_list.append(employee_info)

        resp_c = self.tidb_ob.commit(f'truncate table {EMPLOYEE_DB_TABLE}')  # 清空表
        resp_i = self.tidb_ob.insert(EMPLOYEE_DB_TABLE, EMPLOYEE_FIELD_LIST, employee_list)  # 插入数据
        resp_gdl['data'] = None
        resp_gdel['data'] = None
        resp_gri['data'] = None

        return GeneralResponseSchema(action=return_action,
                                     data=[resp_gdl, resp_gdel, resp_gri, resp_c, resp_i]).to_dict()

    def main(self):
        logger.info('开始同步: 钉钉员工信息')
        resp_gdltt = self.get_department_list_to_tidb()
        resp_gdeltt = self.get_department_employee_list_to_tidb()
        logger.info('同步完成: 钉钉员工信息')
        return GeneralResponseSchema(action='钉钉员工信息同步', data=[resp_gdltt, resp_gdeltt]).to_dict()

if __name__ == '__main__':
    obj = DingdingEmployee()

    print(obj.main())
    # print(obj.get_department_list_to_tidb())
    # print(obj.get_department_employee_list_to_tidb())
