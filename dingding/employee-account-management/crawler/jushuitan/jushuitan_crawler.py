# -*- coding: utf-8 -*-
# @Time     : 2025/1/23 15:57
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : jushuitan_crawler.py
# 聚水潭爬虫
from base import Base
from schema import general_response_decorator


class JushuitanCrawler(Base):
    # 聚水潭用户信息接口
    URL_GET_USER_INFO = 'https://api.erp321.com/erp/webapi/UserDepartmentApi/UserDepartment/GetDetails'
    # 聚水潭用户列表接口
    URL_GET_USER_LIST = 'https://api.erp321.com/erp/webapi/UserDepartmentApi/UserDepartment/PageQueryDepartmentUsers'
    # 聚水潭启用禁用用户接口
    URL_SET_USER_STATUS = 'https://api.erp321.com/erp/webapi/UserDepartmentApi/UserDepartment/ToggleUserStates'

    @general_response_decorator(description='获取聚水潭用户列表', max_retries=3)
    def get_jushuitan_user_info(self, uid: int):
        json_data = {
            'ip': '',
            'uid': '12807669',
            'coid': '10816527',
            'data': {
                'apiVersion': '3.0',
                'type': 'user',
                'id': uid,  # 用户id
            },
        }
        response = self.jushuitan_crawler_session.post(
            self.URL_GET_USER_INFO,
            json=json_data
        )
        return self.check_requests_response(response)['data']

    @general_response_decorator(description='获取聚水潭用户列表', max_retries=3)
    def get_jushuitan_user_list(self):
        json_data = {
            'ip': '',
            'uid': '12807669',
            'coid': '10816527',
            'data': {
                'noRootDept': True,
                'apiVersion': '2.0',
                'deptId': 0,
                'moreFields': True,
            },
            'page': {
                'currentPage': 1,
                'pageSize': 500,
            }
        }
        response = self.jushuitan_crawler_session.post(
            self.URL_GET_USER_LIST,
            json=json_data
        )

        return self.check_requests_response(response)['data']

    @general_response_decorator(description='设置聚水潭用户状态', is_message=1, max_retries=3)
    def set_user_status(self, uid, status: int = 0):
        """
        0 停用,disable / 1 启用,enable 聚水潭用户
        """
        action_type = {
            0: 'disable',
            1: 'enable'
        }
        json_data = {
            'ip': '',
            'uid': '12807669',
            'coid': '10816527',
            'data': {
                'actionType': action_type[int(status)],  # 禁用
                'userIds': [uid]  # 用户id
            },
        }
        # 启用/停用 聚水潭用户
        response = self.jushuitan_crawler_session.post(
            self.URL_SET_USER_STATUS,
            json=json_data
        )

        return self.check_requests_response(response)['data']


if __name__ == '__main__':
    instance = JushuitanCrawler()
    print(instance.set_user_status(15680022, 1))
