# _*_ coding: utf-8 _*_
# @Time : 2023/7/11
# @Author : 张致富
# @Email ： zzf@doocn.com
# @File : crawler-lingxing-fba-data
# @Desc :
from typing import Optional

from pydantic import BaseModel

PROJECT_NAME = "crawler-lingxing-fba-shipmens"
# 补全项目名称(一定要写)
PROJECT_TITLE = "爬虫获取领星FBA货件数据"
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