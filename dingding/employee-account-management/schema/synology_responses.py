# -*- coding: utf-8 -*-
# @Time     : 2024/12/02 16:42
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : synology_responses.py
from io import BytesIO
from typing import Union
from pydantic import BaseModel


class SynologyFileAttributesResponseSchema(BaseModel):
    share_name: Union[str, None]  # 共享盘名称
    remote_path: Union[str, None]  # 远程路径
    file_id: Union[int, str, None]  # 文件ID
    filename: Union[str, None]  # 文件名
    short_name: Union[str, None]  # 短文件名
    create_time: Union[float, int, None]  # 创建时间
    last_access_time: Union[float, int, None]  # 最后访问时间
    last_write_time: Union[float, int, None]  # 最后修改时间
    last_attr_change_time: Union[float, int, None]  # 最后属性修改时间
    file_size: Union[float, int, None]  # 文件大小
    alloc_size: Union[float, int, None]  # 分配大小
    file_attributes: Union[float, int, None]  # 文件属性
    is_directory: Union[bool, None]  # 是否为目录
    is_normal: Union[bool, None]  # 是否为普通文件
    is_readonly: Union[bool, None]  # 是否只读
    bytes_io: Union[BytesIO, None] = None  # 文件内容

    class Config:
        arbitrary_types_allowed = True
