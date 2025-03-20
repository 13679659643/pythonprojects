# -*- coding: utf-8 -*-
# @Time : 2023/08/22
# @Author : 吴宇
# @Email : 2491004019@qq.com
# @File : craw-project-model
# @desc : 接口文件
import importlib
import inspect
import os

import uvicorn
from fastapi import FastAPI, APIRouter
from loguru import logger
from starlette.background import BackgroundTasks

from settings import prefix, PROJECT_TITLE
from digiCore.utils import MsgTool
from digiCore.model import WebEnum, PostItems, ItemEnum

app = FastAPI(docs_url=f'{prefix}/docs',
              redoc_url=f'{prefix}/redoc',
              openapi_url=f'{prefix}/openapi.json', title=PROJECT_TITLE, )

# 接口蓝图
PROJECT_ROUTE = APIRouter(prefix=prefix)
log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"


@PROJECT_ROUTE.get(f"/ping")
async def ping():
    """
    路由测试接口
    :return:
    """
    STATUS_SUCCESS = WebEnum.STATUS_SUCCESS
    return MsgTool.format_api_msg(STATUS_SUCCESS)


def sync_start(item: PostItems, background, route):
    """

    """
    # 必须与 py程序名称一致，如：dim_cd_inv_lx_adjust_end_date_i_d
    sub_server = item.subserver
    operation_type = item.operation_type
    script_path = os.path.join(os.getcwd(), route, f"{sub_server}.py")
    if not os.path.exists(script_path):
        logger.info(f"参数传递错误：{sub_server} !")
        return MsgTool.format_api_msg(WebEnum.STATUS_UNKNOWN)

    # 导入模块 ad_report.crawler_lx_ad_campaign_data
    module_path = f"{route}.{sub_server}"
    module = importlib.import_module(module_path)

    # 从模块中获取类，仅考虑在当前模块中定义的类
    classes = [obj[1] for obj in inspect.getmembers(module, inspect.isclass) if obj[1].__module__ == module.__name__]
    # 实例化找到的第一个类
    instance = classes[0]()
    # 异步启动程序
    extra_params = item.extra_params
    form_uuid = extra_params.get('form_uuid')
    if operation_type == ItemEnum.OPERATION_ASYNC:
        background.add_task(instance.main, form_uuid)
        logger.info("程序异步启动成功！")
    else:
        logger.info("程序同步启动成功！等待程序执行完成")
        instance.main(form_uuid)
        logger.info("程序同步执行完成！")

    return MsgTool.format_api_msg(WebEnum.STATUS_SUCCESS)

@PROJECT_ROUTE.post("/form_table")
async def form_table(item: PostItems, background: BackgroundTasks):
    """
    宜搭-表单
    :param item:
    :param background:
    :return:
    """
    return sync_start(item, background, route='form_table')


@PROJECT_ROUTE.post("/sub_form_table")
async def sub_form_table(item: PostItems, background: BackgroundTasks):
    """
    宜搭-子表单
    :param item:
    :param background:
    :return:
    """
    return sync_start(item, background, route='sub_form_table')

if __name__ == '__main__':
    logger.info('准备开始')
    app.include_router(PROJECT_ROUTE)
    uvicorn.run(app, port=8000, host='0.0.0.0', log_config=log_config)
