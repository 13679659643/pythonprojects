# -*- coding: utf-8 -*-
# @Time    : 2025/2/19 15:25
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:
# 宜搭APi接口-宜搭数据

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool

from schema import GeneralResponseSchema
from script.dingding import TidbQueryDingdingData
from settings import PROJECT_ROUTE

from script.lingxing import TidbQueryLingxingData

# https://api.doocn.com:7000/api/v1/employee-account-management/schedule/apply_for_yida/get_yida_subject_domain
BASE_ROUTE = f"{PROJECT_ROUTE}/apply_for_yida"

router = APIRouter()  # 路由
instance = TidbQueryDingdingData()


@router.get(f"{BASE_ROUTE}/get_yida_app_name")
async def get_app_name_page(request: Request):
    print(dict(request.query_params))
    return await run_in_threadpool(
        instance.get_yida_app_name
    )


# 单选
@router.get(f"{BASE_ROUTE}/get_yida_subject_domain")
async def get_subject_domain_module(request: Request):
    apply_name = '数据集市'  # request.query_params.get('apply_name')

    return await run_in_threadpool(
        instance.get_content_subject_domain,
        apply_name=apply_name
    )


@router.get(f"{BASE_ROUTE}/get_yida_third_level_directory")
async def get_third_level_directory_module(request: Request):
    apply_name = request.query_params.get('apply_name')
    subject_domain = request.query_params.get('subject_domain')

    return await run_in_threadpool(
        instance.get_content_third_level_directory,
        apply_name=apply_name,
        subject_domain=subject_domain
    )


@router.get(f"{BASE_ROUTE}/get_yida_form_name")
async def get_form_name_module(request: Request):
    apply_name = request.query_params.get('apply_name')
    subject_domain = request.query_params.get('subject_domain')
    third_level_directory = request.query_params.get('third_level_directory')

    return await run_in_threadpool(
        instance.get_content_form_name,
        apply_name=apply_name,
        subject_domain=subject_domain,
        third_level_directory=third_level_directory
    )
