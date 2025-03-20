# -*- coding: utf-8 -*-
# @Time     : 2024/12/28 09:42
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : responses.py
from pydantic import BaseModel
from typing import Union, Any
from schema.enums import ResponseStatus


class GeneralResponseSchema(BaseModel):
    code: int
    success: Union[bool, None]
    description: Union[str, None]
    message: Union[Any, None]
    data: Union[Any, None]

    def __init__(
            self,
            code: int = 0,  # 默认状态码为 0
            success: Union[bool, None] = None,
            description: Union[str, None] = None,
            message: Union[Any, None] = None,
            data: Union[Any, None] = None,
            response_status: Union[Any, None] = ResponseStatus,
    ):
        """
        通用响应数据模型。

        :param code: 响应码, 默认0
        :param success: 成功状态, 默认True或False
        :param description: 功能描述, 默认None
        :param message: 响应消息, 默认None
        :param data: 响应数据, 默认None
        """
        if not isinstance(code, int):
            raise ValueError('code 必须是整数!')
        status = response_status.from_code(code)
        super().__init__(
            code=code,
            success=success if success is not None else status.success,
            description=description,
            message=[status.message, message],
            data=data
        )

    def to_dict(self) -> dict:
        """
        将响应对象转换为字典。

        :return: 包含响应信息的字典
        """
        return {
            'code': self.code,
            'success': self.success,
            'description': self.description,
            'message': self.message,
            'data': self.data
        }
