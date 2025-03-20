# -*- coding: utf-8 -*-
# @Time     : 2024/12/28 09:38
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : decorators.py
import time
from typing import Union, Callable

from schema.enums import ResponseStatus
from schema.responses import GeneralResponseSchema


def general_response_decorator(
        code: int = 0,
        success: Union[str, None] = None,
        description: Union[str, None] = None,
        message: Union[str, None] = None,
        is_message: Union[bool, int, None] = False,
        max_retries: int = 0,
        delay: int = 2
) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> GeneralResponseSchema:
            error_count = 0
            func_name = func.__qualname__
            payload = {
                'code': code,
                'success': success,
                'description': description if description is not None else f'{func_name}',
                'message': message,
                'data': None
            }
            while True:
                try:
                    # 成功时调用GeneralResponseSchema并返回
                    res = func(*args, **kwargs)
                    if is_message:
                        payload['message'] = res
                    else:
                        payload['data'] = res
                    break
                except Exception as e:
                    if max_retries == error_count:
                        # 异常时打印堆栈信息并返回错误响应
                        # traceback.print_exc()
                        payload['code'] = ResponseStatus.FUNCTION_ERROR.code
                        error_content = f'方法报错: {func_name}\n\t{str(e)}'
                        payload['message'] = f'{message}:\n\t{error_content}' if message else error_content
                        break
                    time.sleep(delay)  # 等待
                    error_count += 1
            return GeneralResponseSchema(**payload)

        return wrapper

    return decorator
