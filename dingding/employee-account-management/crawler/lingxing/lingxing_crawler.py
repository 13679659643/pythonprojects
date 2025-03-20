# -*- coding: utf-8 -*-
# @Time     : 2025/1/23 17:14
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : lingxing_crawler.py
import json
from typing import Union, List, Dict, Any, Optional
from base import Base
from schema import general_response_decorator, GeneralResponseSchema


class LingxingCrawler(Base):
    URL_GET_USER_INFO = 'https://gw.lingxingerp.com/newadmin/api/user/manage/getMember'
    URL_GET_USER_LIST = 'https://gw.lingxingerp.com/newadmin/api/user/manage/page'
    URL_SET_USER_STATUS = 'https://gw.lingxingerp.com/newadmin/api/user/manage/setStatus'
    # 角色列表
    URL_GET_ROLE_LIST = 'https://gw.lingxingerp.com/newadmin/role/list?req_time_sequence=%2Fnewadmin%2Frole%2Flist$$7'
    # 角色用户列表
    URL_GET_ROLE_USER_LIST = 'https://gw.lingxingerp.com/newadmin/role/users?gid=10080378&req_time_sequence=%2Fnewadmin%2Frole%2Fusers$$2'
    # 获取领星功能\字段权限
    URL_GET_ROLE_PERMISSION = 'https://gw.lingxingerp.com/newadmin/permission/r'
    # 获取领星数据权限
    URL_GET_ROLE_DATA_PERMISSION = 'https://gw.lingxingerp.com/newadmin/data/r-permission'

    @general_response_decorator(description='获取领星用户信息')
    def get_user_info(self, uid) -> GeneralResponseSchema:
        params = {
            'user_id': uid,  # 201814
            'req_time_sequence': '/newadmin/api/user/manage/getMember$$1'
        }
        response = self.lingxing_crawler_session.get(self.URL_GET_USER_INFO, params=params)

        return self.check_requests_response(response)['data']

    @general_response_decorator(description='获取领星用户列表')
    def get_user_list(self) -> GeneralResponseSchema:
        params = {
            'pageNo': 1,
            'pageSize': 1000,
            'status': '',
            'orgIds': '',
            'roleIds': '',
            'sort_field': 'create_time',
            'sortType': 'desc',
            'req_time_sequence': '/newadmin/api/user/manage/page$$5'
        }
        response = self.lingxing_crawler_session.get(self.URL_GET_USER_LIST, params=params)

        return self.check_requests_response(response)['list']

    @general_response_decorator(description='设置领星用户状态', is_message=1)
    def set_user_status(self, uid, status: int = 0) -> GeneralResponseSchema:
        json_data = {
            'uidList': [str(uid)],
            'status': status,
            'req_time_sequence': '/newadmin/api/user/manage/setStatus$$1'
        }
        response = self.lingxing_crawler_session.post(self.URL_SET_USER_STATUS, json=json_data)

        return self.check_requests_response(response)

    @general_response_decorator(description='获取领星角色列表')
    def get_role_list(self) -> GeneralResponseSchema:
        response = self.lingxing_crawler_session.get(self.URL_GET_ROLE_LIST)
        # 处理异常逻辑:请求失败: 请求失败, 返回状态码: 404, 返回内容: {"error": "Not Found"}
        return self.check_requests_response(response)['list']

    @general_response_decorator(description='获取领星角色用户列表')
    def get_role_user_list(self, id='10190547') -> GeneralResponseSchema:
        new_url = self.URL_GET_ROLE_USER_LIST.replace('10080378', str(id))
        response = self.lingxing_crawler_session.get(new_url)
        return self.check_requests_response(response)['users']

    def module_permission_analysis(self, page_name: str, rules: list, role_id: str, data_perms: dict, func_perms_select: list):
        for rule in rules:
            if 'rules' not in rule:
                data = {
                    'id': role_id,
                    'perm_id': rule['id'],
                    'page_name': page_name,
                    'module': rule['module'],
                    'action': rule['action'],
                    'action_child': rule['action_child'],
                    'title': rule['title'],
                    'name': rule['name'],
                    'category': rule['category'],
                    'sort': rule['sort'],
                    'action_sort': rule['action_sort'],
                    'is_select_perms': 1 if str(rule['id']) in func_perms_select else 0,  # 功能权限是否勾选(1:已勾选,0:没有勾选)
                    'select_perms_json': json.dumps(func_perms_select),  # 已勾选的功能权限json格式
                    'cg_price': data_perms.get('cg_price', None),  # 采购成本(1:可见,0:不可见,2:仅跟进人可见)
                    'ware_house_price_amount': data_perms.get('ware_house_price_amount', None),  # 库存单价、库存货值
                    'supplier': data_perms.get('supplier', None),  # 供应商
                    'lg_cost': data_perms.get('lg_cost', None),  # 物流费用
                }
                yield data
                continue
            yield from self.module_permission_analysis(page_name, rule['rules'], role_id, data_perms, func_perms_select)

    @general_response_decorator(description='获取领星功能\字段权限')
    def get_role_action_perm(self, role_id: Union[int, str] = 10080378) -> GeneralResponseSchema:
        params = {
            'id': role_id,
            'req_time_sequence': '/newadmin/permission/r$$9'
        }
        response = self.lingxing_crawler_session.get(self.URL_GET_ROLE_PERMISSION, params=params)
        data = self.check_requests_response(response)['data']
        data_perms = data['data_perms']

        func_perms: dict = data['func_perms']
        amazon_func_perms: list = func_perms['amazon']['list']
        multi_func_perms: list = func_perms['multi']['list']

        func_perms_select = []
        func_perms_select.extend(func_perms['amazon']['selected'])
        func_perms_select.extend(func_perms['multi']['selected'])

        rules = []
        for module_permission in amazon_func_perms:
            rules.extend(self.module_permission_analysis('亚马逊', module_permission['actions'], role_id, data_perms, func_perms_select))
        for module_permission in multi_func_perms:
            rules.extend(self.module_permission_analysis('多平台', module_permission['actions'], role_id, data_perms, func_perms_select))
        return {'func_perms': rules, 'func_perms_select': func_perms_select, 'data_perms': data_perms}

    def module_data_analysis(self, module_permission: dict):
        type_name = module_permission.get('type_name', 'None') + '数据权限'
        id = module_permission.get('group_id', None)
        permission_org = json.dumps(module_permission.get('permission_org', None))
        permission_owner = json.dumps(module_permission.get('permission_owner', None))
        type_us = module_permission.get('type', None)

        rules_data_perm = []
        for module in module_permission['all_module']:
            module_name = module.get('module_name', None)
            data_perm = [{'type_name': type_name,
                          'id': id,
                          'permission_org': permission_org,
                          'permission_owner': permission_owner,
                          'type': type_us,
                          'module_name': module_name,
                          **sub} for sub in module['sub_unit']]
            rules_data_perm.extend(data_perm)

        return rules_data_perm

    # 获取数据权限
    @general_response_decorator(description='获取领星数据权限')
    def get_role_data_perm(self, role_id: Union[int, str] = 10080378) -> list[dict[str, Optional[Any]]]:
        params = {
            'group_id': role_id,
            'req_time_sequence': '/newadmin/data/r-permission/$$8'
        }
        response = self.lingxing_crawler_session.get(self.URL_GET_ROLE_DATA_PERMISSION, params=params)
        data = self.check_requests_response(response)['data']
        data_perms = data['configs']

        rules = []
        for module_permission in data_perms:
            rules.extend(self.module_data_analysis(module_permission))

        return rules


if __name__ == '__main__':
    from common import Utils

    instance = LingxingCrawler()

    resp = instance.get_user_info('10654761')
    print(resp)
    # # resp = instance.get_role_user_list()
    # resp = instance.get_role_action_perm()
    # resp = instance.get_role_data_perm()
    # resp.to_dict()
    #
    # # resp = instance.get_role_action_perm(10496732)
    # print(resp)
    # print(type(resp))
    # exit()
    # for item in resp.data['func_perms']:
    #     print(item)
    # for item in resp.data['func_perms_select']:
    #     print(item)
    # # print(resp.data.keys())
