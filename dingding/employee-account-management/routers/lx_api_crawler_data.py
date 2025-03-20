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
from starlette.background import BackgroundTasks

from script.lingxing.tidb_insert_lingxing_data import TidbInsertLingxingData
from settings import PROJECT_ROUTE

BASE_ROUTE = f"{PROJECT_ROUTE}/lx_for_crawler"

router = APIRouter()  # 路由
instance = TidbInsertLingxingData()


@router.get(f"{BASE_ROUTE}/insert_user_list")
async def api_insert_user_list():
    return await run_in_threadpool(
        instance.insert_user_list
    )


@router.get(f"{BASE_ROUTE}/insert_user_info")
async def api_insert_user_info():
    return await run_in_threadpool(
        instance.insert_user_info
    )


@router.get(f"{BASE_ROUTE}/insert_user_mapping_store")
async def api_insert_user_mapping_store():
    return await run_in_threadpool(
        instance.insert_user_mapping_store
    )


@router.get(f"{BASE_ROUTE}/insert_role_data")
async def api_insert_role_data():
    return await run_in_threadpool(
        instance.insert_role_data
    )


@router.get(f"{BASE_ROUTE}/insert_role_user_data")
async def api_insert_role_user_data():
    return await run_in_threadpool(
        instance.insert_role_user_data
    )


@router.get(f"{BASE_ROUTE}/insert_role_action_perm")
async def api_insert_role_action_perm(background: BackgroundTasks):
    # return await run_in_threadpool(
    #     instance.insert_role_action_perm
    # )
    # 异步采集数据，接口调用瞬间完成，服务器异步同步。
    background.add_task(instance.insert_role_action_perm)

    return {'code': 0}


@router.get(f"{BASE_ROUTE}/insert_role_data_perms")
async def api_insert_role_data_perms():
    return await run_in_threadpool(
        instance.insert_role_data_perms
    )
