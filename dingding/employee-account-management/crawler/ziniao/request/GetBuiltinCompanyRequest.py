#!/usr/bin/python
# -*- coding: UTF-8 -*-
from crawler.ziniao.common import RequestTypes
from crawler.ziniao.request.BaseRequest import BaseRequest


class GetBuiltinCompanyRequest(BaseRequest):
    """获取当前自建应用的公司信息"""

    def __init__(self):
        BaseRequest.__init__(self)

    def get_method(self):
        return '/app/builtin/company'

    def get_request_type(self):
        return RequestTypes.GET
