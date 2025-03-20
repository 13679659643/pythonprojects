# -*- coding: utf-8 -*-
# @Time     : 2024/11/25 15:57
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : __init__.py.py

from loguru import logger
from typing import Any, Optional, Callable
from crawler.ziniao.client.api_config import Config
from crawler.ziniao.client.create_client import client
from crawler.ziniao.request.AppTokenRequest import AppTokenRequest
from crawler.ziniao.request.ERPStaffQueryRequest import ERPStaffQueryRequest
from crawler.ziniao.request.ERPStaffDisableRequest import ERPStaffDisableRequest

from base import Base
from schema import general_response_decorator


class ZiniaoApi(Base):
    status_mapping = {
        0: (1, '停用'),  # 停用, 紫鸟 1
        '0': (1, '停用'),  # 停用, 紫鸟 1
        1: (0, '启用'),  # 启用, 紫鸟 0
        '1': (0, '启用'),  # 启用, 紫鸟 0
        2: (2, '删除'),  # 删除, 紫鸟 2
        '2': (2, '删除'),  # 删除, 紫鸟 2
    }

    @property
    def app_token(self):
        """
        紫鸟 app-auth-token

        """
        response = client.execute(AppTokenRequest())
        return response.data.get('appAuthToken') if response.is_success() else ''

    @general_response_decorator(action='获取紫鸟用户列表')
    def get_user_list(self) -> Optional[Any]:
        """
        获取紫鸟所有用户

        """
        result = client.execute(ERPStaffQueryRequest(), app_token=self.app_token)
        data_list = []
        if result.is_success():
            for item in result.data.get('data'):
                data = dict(
                    userid=item.get('userId'),
                    username=item.get('username'),
                    fullname=item.get('name'),
                    mobile='' if item.get('mobile') is None else item.get('mobile').replace('+86-', ''),
                    auth_phone=item.get('authPhone'),
                    level='' if item.get('level') is None else item.get('level'),
                    status=self.status_mapping.get(item.get('delflag'))[0],
                )
                data_list.append(data)

        return data_list

    @general_response_decorator(action='设置紫鸟用户状态')
    def disable_user(self, uid: str, status: int = 0, **kwargs):
        """
        本地账号启用禁用参数

        """

        # raise NotImplementedError('报错测试!')
        username = kwargs.get('username', '未知用户?')
        fullname = kwargs.get('fullname', '未知姓名?')
        return_data = {
            'uid': uid,
            'username': username,
            'fullname': fullname,
            'status_value': self.status_mapping.get(status)[1]
        }

        request = ERPStaffDisableRequest()
        request.biz_model = {
            'companyId': Config.company_id,
            'staffIds': [str(uid)],
            'status': str(self.status_mapping.get(status)[0])
        }
        response = client.execute(request, app_token=self.app_token)

        # logger.info(f'紫鸟用户 [{username} {fullname}] 已{self.status_mapping.get(status)[1]}')
        return_data.update(response.data)

        return return_data


if __name__ == '__main__':
    obj = ZiniaoApi()

    user_list = obj.get_user_list()
    #
    for item in user_list:
        print(item)

    # print(obj.disable_user(uid='17320838845187', status=0))
