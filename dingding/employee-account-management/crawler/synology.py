# -*- coding: utf-8 -*-
# @Time     : 2024/11/26 14:03
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : synology.py
# import requests
import copy
import json
import traceback
from loguru import logger
from requests import Session

from base import Base
from schema import general_response_decorator


class SynologyApi(Base):
    def __init__(self, host, port, ssh_ip, ssh_port, username, password, https=True, maximum_retry=2):
        super().__init__()
        self.host = host
        self.port = port
        self.ssh_ip = ssh_ip
        self.ssh_port = str(ssh_port)
        self.username = username
        self.password = password
        self.maximum_retry = maximum_retry
        self.synology_url = f'https://{self.host}:{self.port}' if https else f'http://{self.host}:{self.port}'
        self.url = f'{self.synology_url}/webapi/entry.cgi'

        self.sid = None

        self.login_status = False
        self.synology_api_session = Session()

    def _login(self):
        synology_login_payload = {
            'api': 'SYNO.API.Auth',
            'version': '7',
            'method': 'login',
            'account': self.username,
            'passwd': self.password,
            'session': 'webui',
            'format': 'sid',
            'enable_syno_token': 'yes',
            'timezone': '+08:00',
            'logintype': 'local'
        }

        maximum_retry = copy.copy(self.maximum_retry)
        login_url = f'{self.synology_url}/webapi/auth.cgi'

        self.synology_api_session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        while not self.login_status and maximum_retry > 0:
            try:
                response = self.synology_api_session.post(login_url, data=synology_login_payload)
                # print(response.json())
                login_result = response.json()
                self.login_status = login_result['success']
                if self.login_status:
                    login_data = login_result['data']
                    self.synology_api_session.cookies.set('id', login_data['sid'])
                    self.synology_api_session.headers.update({'X-Syno-Token': login_data['synotoken']})
                    self.sid = login_data['sid']
                    # logger.success(f'登录成功[{self.host},{self.username}]')
                    break
                else:
                    maximum_retry -= 1
                    logger.error(
                        f'登录失败[{self.host},{self.username}], 剩余尝试次数: {maximum_retry}, 错误信息: {login_result}')
            except Exception as e:
                self.login_status = False
                maximum_retry -= 1
                traceback.print_exc()
                logger.error(
                    f'登录失败[{self.host},{self.username}], 剩余尝试次数: {maximum_retry}, 错误信息: \n{traceback.format_exc()}')
        if not self.login_status and maximum_retry == 0:
            logger.error(f'登录失败[{self.host},{self.username}], 已达到最大重试次数')

    def _logout(self) -> None:
        logout_url = f'{self.synology_url}/webapi/auth.cgi'
        param = {'api': 'SYNO.API.Auth', 'version': '7', 'method': 'logout', 'session': 'webui'}

        response = self.synology_api_session.get(logout_url, params=param)

        if self.check_response_code(response):
            if response.json()['success']:
                self.login_status = False
                # logger.success(f'退出成功[{self.host},{self.username}]')
                return

        logger.error(f'退出失败[{self.host},{self.username}]')

    def __enter__(self):
        self._login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._logout()

    def check_login_status(self):
        if not self.login_status:
            raise ValueError('登录失败!')

    @general_response_decorator(action='获取群晖用户信息')
    def get_user_info(self, name):
        self.check_login_status()
        compound = [
            {
                "api": "SYNO.Core.User",
                "method": "get",
                "version": 1,
                "name": name,
                "additional": ["description", "email", "expired"]
            }
        ]
        payload = {
            'api': 'SYNO.Entry.Request',
            'method': 'request',
            'version': '1',
            'stop_when_error': 'false',
            'mode': '"sequential"',
            'compound': json.dumps(compound, ensure_ascii=False)
        }
        response = self.synology_api_session.post(self.url, data=payload)
        assert response.status_code == 200, response.text
        return response.json()['data']['result'][0]

    @general_response_decorator(action='获取群晖用户列表')
    def get_user_list(self):
        self.check_login_status()

        payload = {
            'api': 'SYNO.Core.User',
            'method': 'list',
            'version': 1,
            'type': 'local',
            'offset': 0,
            'limit': -1,
            'additional': '["uid","name","description","email","expired"]',
        }
        response = self.synology_api_session.post(self.url, data=payload)
        assert response.status_code == 200
        user_list = response.json()['data']['users'] if response.json()['success'] else response.json()

        return user_list

    @general_response_decorator(action='设置群晖用户状态')
    def modify_user(self, username, status):
        """
        修改群晖用户信息
        默认功能是"停用群晖用户"

        :param username: 姓名
        :param status: 用户状态  1: 正常, 0: 停用
        :return:
        """
        status_mapping = {
            1: 0,
            '1': 0,
            0: 1,
            '0': 1
        }
        # 获取该用户信息
        resp_gui = self.get_user_info(username)
        user = resp_gui['data'].get('data', {}).get('users', [])
        assert user, f'用户[{username}]不存在'
        user = user[0]
        fullname = user['description']  # 当前用户全名
        email = user['email']  # 当前用户电子邮件
        # 调用ssh修改
        command = f'synouser --modify {username} "{fullname}" {status_mapping[status]} {email}'
        with self.ssh_client(host=self.ssh_ip, port=self.ssh_port, username=self.username,
                             password=self.password) as ssh:
            response = ssh.execute(command, sudo=True)
        # 返回用户信息
        resp_gui = self.get_user_info(username)
        user = resp_gui['data'].get('data', {}).get('users', [])[0]
        return user


if __name__ == '__main__':
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
    with SynologyApi(**SYNOLOGY_CONFIG['chengdu']) as syno:
        pass

