# -*- coding: utf-8 -*-
# @Time     : 2024/12/30 09:45
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : log_config.py
from uvicorn.logging import AccessFormatter
from .global_state import global_state


class CustomAccessFormatter(AccessFormatter):
    def format(self, record):
        record.real_ip = global_state.real_id
        return super().format(record)
