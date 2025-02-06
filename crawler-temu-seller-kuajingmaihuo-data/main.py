# -*- coding: utf-8 -*-
# @Time    : 2024/12/18 14:21
# @Author  : Night
# @File    : main.py
# @Description:
import importlib
import inspect
import uvicorn
from digiCore.common.setting import PostItems, ItemEnum, Status
from fastapi import FastAPI, BackgroundTasks
from loguru import logger

from settings import PROJECT_ROUTE, PROJECT_TITLE

app = FastAPI(docs_url=f'{PROJECT_ROUTE}/docs',
              redoc_url=f'{PROJECT_ROUTE}/redoc',
              openapi_url=f'{PROJECT_ROUTE}/openapi.json', title=PROJECT_TITLE, )

log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"


@app.get(f"{PROJECT_ROUTE}/ping")
async def ping():
    """
    路由测试接口
    :return:
    """
    return Status.describe(Status.OK)


@app.post(f"{PROJECT_ROUTE}")
async def sync_start(item: PostItems, background: BackgroundTasks):
    """
    启动同步-统计数据
    判断程序是否启动
    :param background:
    :return:
    """
    # 子服务名称 必须与 py程序名称一致。
    sub_server = item.subserver
    platform_name = item.extra_params.get('platform_name', '')
    module_path = f"{platform_name}.{sub_server}"
    operation_type = item.operation_type
    module = importlib.import_module(module_path)
    # 判断sub_server是否存在对应得py文件
    classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass) if obj.__module__ == module_path]
    if not classes:
        logger.info(f"参数传递错误：{module_path} !")
        return Status.describe(Status.NOT_FOUND)
    instance = classes[0]()
    hasattr(instance, 'main')
    # 异步启动程序
    if operation_type == ItemEnum.OPERATION_ASYNC:
        background.add_task(instance.main, )
        logger.info("程序异步启动成功！")
        return Status.describe(Status.OK)
    else:
        logger.info("程序同步启动成功！等待程序执行完成")
        instance.main()
        logger.info("程序同步执行完成！")
        return Status.describe(Status.OK)


if __name__ == '__main__':
    logger.info('准备开始')
    uvicorn.run(app, port=8000, host='0.0.0.0', log_config=log_config)
