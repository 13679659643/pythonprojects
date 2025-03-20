# -*- coding: utf-8 -*-
# @Time     : 2025/1/24 15:13
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : yida_api_lingxing_data.py
# 宜搭APi接口-领星数据

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool

from schema import GeneralResponseSchema
from settings import PROJECT_ROUTE
from script.lingxing import TidbQueryLingxingData

BASE_ROUTE = f"{PROJECT_ROUTE}/apply_for_role"

router = APIRouter()  # 路由
instance = TidbQueryLingxingData()


@router.get(f"{BASE_ROUTE}/get_lingxing_role_page")
async def get_role_page(request: Request):
    print(dict(request.query_params))
    return await run_in_threadpool(
        instance.get_role_page_data
    )


@router.get(f"{BASE_ROUTE}/get_lingxing_role_module")
async def get_role_module(request: Request):
    page_name = request.query_params.get('page_name')
    real_name = request.query_params.get('real_name')

    return await run_in_threadpool(
        instance.get_role_module_data,
        page_name=page_name,
        real_name=real_name
    )


@router.get(f"{BASE_ROUTE}/get_lingxing_role_action")
async def get_role_action(request: Request):
    page_name = request.query_params.get('page_name')
    module_name = request.query_params.get('module_name')
    real_name = request.query_params.get('real_name')

    return await run_in_threadpool(
        instance.get_role_action_data,
        page_name=page_name,
        module_name=module_name,
        real_name=real_name
    )


@router.get(f"{BASE_ROUTE}/get_lingxing_role_perm")
async def get_role_perm(request: Request):
    page_name = request.query_params.get('page_name')
    module_name = request.query_params.get('module_name')
    action_name = request.query_params.get('action_name')
    real_name = request.query_params.get('real_name')

    return await run_in_threadpool(
        instance.get_role_perm_data,
        page_name=page_name,
        module_name=module_name,
        action_name=action_name,
        real_name=real_name
    )


# https://api.doocn.com:7000/api/v1/employee-account-management/schedule/apply_for_role/get_lingxing_store_platform


@router.get(f"{BASE_ROUTE}/get_lingxing_store_platform")
async def get_store_platform(request: Request):
    return await run_in_threadpool(
        instance.get_store_platform_data
    )


@router.get(f"{BASE_ROUTE}/get_lingxing_store_list")
async def get_store_list(request: Request):
    platform_code = request.query_params.get('platform_code')

    if str(platform_code) == 'Amazon':
        return await run_in_threadpool(
            instance.get_amazon_store_data
        )
    return await run_in_threadpool(
        instance.get_mutil_platform_store_data,
        platform_code=platform_code
    )


@router.get(f"{BASE_ROUTE}/get_lingxing_store_site")
async def get_store_list(request: Request):
    platform_code = request.query_params.get('platform_code')
    store = request.query_params.get('store')

    return await run_in_threadpool(
        instance.get_amazon_store_site,
        platform_code=platform_code,
        store=store
    )


@router.get(f"{BASE_ROUTE}/get_lingxing_user_info")
async def get_user_info(request: Request):
    real_name = request.query_params.get('real_name')

    return await run_in_threadpool(
        instance.get_user_info_data,
        real_name=real_name
    )
