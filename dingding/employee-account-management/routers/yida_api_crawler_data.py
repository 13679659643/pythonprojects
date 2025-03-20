# -*- coding: utf-8 -*-
# @Time    : 2025/2/19 15:25
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:
# 采集APi接口-lx、宜搭
import logging

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from script.dingding.tidb_insert_dingding_data import TidbInsertDingdingData
from settings import PROJECT_ROUTE


BASE_ROUTE = f"{PROJECT_ROUTE}/yida_for_crawler"

router = APIRouter()  # 路由
instance = TidbInsertDingdingData()


@router.get(f"{BASE_ROUTE}/insert_yida_application_contents")
async def api_insert_yida_application_contents():
    return await run_in_threadpool(
        instance.insert_yida_application_contents
    )