#!/usr/bin/python
# -*- coding: UTF-8 -*-
from crawler.ziniao.common import RequestTypes
from crawler.ziniao.request.BaseRequest import BaseRequest


class AppTokenRequest(BaseRequest):
    """获取应用token请求"""

    def __init__(self):
        BaseRequest.__init__(self)

    def get_method(self):
        return '/auth/get_app_token'

    def get_request_type(self):
        return RequestTypes.POST_JSON
