# -*- coding: utf-8 -*-
# @Time    : 2024/12/26 9:19
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:
from typing import Optional

from pydantic import BaseModel

PROJECT_NAME = "crawler-lingxing-mutil-channel-data"
# 补全项目名称(一定要写)
PROJECT_TITLE = "爬虫获取领星多平台Temu在线商品"
# 接口路由
PROJECT_ROUTE = f"/api/v1/{PROJECT_NAME}/schedule"


class PostItems(BaseModel):
    """
    传参
    """
    service_name: str
    subserver: str
    operation_type: Optional[str] = 'sync'  # sync:同步，async:异步， 默认同步
    run_sign: Optional[str] = 'start'  # start:启动，stop:停止， 默认启动
    extra_params: Optional[dict] = {}  # 额外传参