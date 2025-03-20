# -*- coding: utf-8 -*-
# @Time     : 2024/12/28 09:47
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : enums.py
from enum import Enum


class ResponseStatus(Enum):
    SUCCESS = (0, True, '响应成功!')
    FAILURE = (1, False, '响应失败!')
    UNKNOWN = (2, False, '未知结果?')
    FUNCTION_ERROR = (9, False, '程序异常?')
    DATABASE_ERROR = (10, False, '数据库异常?')

    def __init__(self, code: int, success: bool, message: str):
        self.code = code
        self.success = success
        self.message = message

    @classmethod
    def from_code(cls, code: int):
        for status in cls:
            if status.code == code:
                return status
        return cls.UNKNOWN
