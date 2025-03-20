# -*- coding: utf-8 -*-
# @Time     : 2024/10/19 09:49
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : real_ip_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from settings import global_state


class RealIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 尝试从请求头中获取真实IP地址，如果获取失败则使用请求客户端的主机地址
        global_state.real_id = request.headers.get('X-Forwarded-For', request.client.host) or 'unknown'
        # 调用下一个中间件或处理程序，并返回相应的响应
        response = await call_next(request)
        return response
