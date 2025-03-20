# -*- coding: utf-8 -*-
from requests import Response

from base.ob import Ob


class Base(Ob):
    # 检测响应码
    def check_requests_response(self, response: Response, is_json: bool = True):
        assert response.ok, f'请求失败, 返回状态码: {response.status_code}, 返回内容: {response.text}'
        if is_json:
            return response.json()
        return response.text
