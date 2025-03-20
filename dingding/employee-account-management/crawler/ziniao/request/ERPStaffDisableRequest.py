#!/usr/bin/python
# -*- coding: UTF-8 -*-
from crawler.ziniao.common import RequestTypes
from crawler.ziniao.request.BaseRequest import BaseRequest


class ERPStaffDisableRequest(BaseRequest):
    """ERP-员工查询"""

    def __init__(self):
        BaseRequest.__init__(self)
        self.biz_model = {
            "companyId": "16143623234860",
            "staffIds": [],
            "status": "1"
        }

    def get_method(self):
        return '/superbrowser/rest/v1/erp/staff/status'

    def get_request_type(self):
        return RequestTypes.POST_JSON
