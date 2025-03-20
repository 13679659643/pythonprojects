# -*- coding: utf-8 -*-
# @Time     : 2024/09/25 17:34
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : ob.py
# from loguru import logger
from requests import Session
from digiCore.db.redis.core import RedisDao

from .customize_tidb import MyTiDBDao
from .ssh_client import SSHConnection
from .smb_client import SMBClient
from .constants import *


class Ob:
    def __init__(self):
        self._redis_ob = None
        self._tidb_ob = None

        self._lingxing_crawler_session = None
        self._jushuitan_crawler_session = None
        self._dingding_api_session = None
        self._npm_crawler_session = None

    @property
    def ssh_client(self):
        return SSHConnection

    @property
    def smb_client(self):
        return SMBClient

    @property
    def redis_ob(self) -> RedisDao:
        if self._redis_ob is None:
            self._redis_ob = RedisDao()

        return self._redis_ob

    @property
    def tidb_ob(self) -> MyTiDBDao:
        if self._tidb_ob is None:
            self._tidb_ob = MyTiDBDao()

        return self._tidb_ob

    @property
    def lingxing_crawler_session(self) -> Session:
        if self._lingxing_crawler_session is None:
            self._lingxing_crawler_session = Session()
            LINGXING_CRAWLER_HEADERS.update({'auth-token': self.redis_ob.get_lingxing_crawler_auth_token()})
            self._lingxing_crawler_session.headers.update(LINGXING_CRAWLER_HEADERS)

        return self._lingxing_crawler_session

    @property
    def jushuitan_crawler_session(self) -> Session:
        if self._jushuitan_crawler_session is None:
            self._jushuitan_crawler_session = Session()
            self._jushuitan_crawler_session.headers.update(JUSHUITAN_CRAWLER_HEADERS)
            self._jushuitan_crawler_session.cookies.update(self.redis_ob.get_erp321_cookie())

        return self._jushuitan_crawler_session

    @property
    def dingding_api_session(self) -> Session:
        if self._dingding_api_session is None:
            self._dingding_api_session = Session()
            self._dingding_api_session.headers.update(DINGDING_API_HEADERS)
            self._dingding_api_session.headers.update(
                {'x-acs-dingtalk-access-token': self.redis_ob.get_dingding_access_token()})

        return self._dingding_api_session

    # @property
    # def npm_crawler_session(self) -> Session:
    #     if self._npm_crawler_session is None:
    #         self._npm_crawler_session = Session()
    #         self._npm_crawler_session.headers.update(NPM_CRAWLER_HEADERS)
    #         response = self._npm_crawler_session.post(NPM_CRAWLER_LOGIN_URL, json=NPM_CRAWLER_LOGIN_DATA)
    #         if response.status_code != 200:
    #             logger.error(f'登录失败: {response.text}')
    #         else:
    #             result = response.json()
    #             self._npm_crawler_session.headers.update({'Authorization': f'Bearer {result["token"]}'})
    #
    #     return self._npm_crawler_session
