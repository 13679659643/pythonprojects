# -*- coding: utf-8 -*-
import uvicorn
import inspect
import warnings
import importlib
import traceback

from loguru import logger
from fastapi import FastAPI, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from digiCore.common.setting import PostItems
from starlette.middleware.cors import CORSMiddleware
from cryptography.utils import CryptographyDeprecationWarning

from middleware.real_ip_middleware import RealIPMiddleware
from schema import GeneralResponseSchema, ResponseStatus
from settings import CustomAccessFormatter
from settings import PROJECT_ROUTE, PROJECT_TITLE

from routers import yida_api_lingxing_data, yida_api_dingding_data, yida_api_crawler_data, lx_api_crawler_data

# 忽略特定类型的警告
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

app = FastAPI(
    docs_url=f'{PROJECT_ROUTE}/docs',
    redoc_url=f'{PROJECT_ROUTE}/redoc',
    openapi_url=f'{PROJECT_ROUTE}/openapi.json',
    title=PROJECT_TITLE,
)

app.add_middleware(RealIPMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tgyn0g.aliwork.com", 'https://www.aliwork.com'],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

app.include_router(yida_api_lingxing_data.router)
app.include_router(yida_api_dingding_data.router)
app.include_router(yida_api_crawler_data.router)
app.include_router(lx_api_crawler_data.router)

log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["()"] = CustomAccessFormatter
log_config["formatters"]["access"][
    "fmt"] = "%(asctime)s - %(levelname)s - %(real_ip)s - %(request_line)s - %(status_code)s"


@app.get(f"{PROJECT_ROUTE}/ping")
async def ping():
    """
    路由测试接口
    :return:
    """

    return GeneralResponseSchema(description='路由测试接口')


@app.post(PROJECT_ROUTE)
async def sync_start(item: PostItems, background: BackgroundTasks):
    """
    启动同步-统计数据
    判断程序是否启动
    :param background:
    :return:
    """
    # 子服务名称 必须与 py程序名称一致。
    sub_server = item.subserver
    sub_server = f'script.{sub_server}'  # 子服务存在script目录下
    operation_type = item.operation_type
    operation_title = '异步' if operation_type == 'async' else '同步'
    logger.info(f"开始{operation_title}启动子服务：{sub_server}")
    code = ResponseStatus.SUCCESS.code
    description = f"{operation_title}启动程序"
    message = None
    data = None
    try:
        # 判断sub_server是否存在对应得py文件
        module = importlib.import_module(sub_server)
        classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass) if obj.__module__ == sub_server]
        assert len(classes) > 0, f"{sub_server}缺少类"
        # 实例化子服务
        instance = classes[0]()
        # 判断是否有main方法
        assert hasattr(instance, 'main'), f"{sub_server}没有main方法"
        # 启动程序 异步/同步
        if operation_type == 'async':
            background.add_task(instance.main)
        else:
            data = await run_in_threadpool(instance.main)
        logger.success(f"{classes[0]} 启动完成!")
    except Exception as e:
        code, message = ResponseStatus.FUNCTION_ERROR.code, str(e)
        traceback.print_exc()
    finally:
        return GeneralResponseSchema(code=code, description=description, message=message, data=data)


if __name__ == '__main__':
    logger.info('准备开始')
    uvicorn.run(app, port=8000, host='0.0.0.0', log_config=log_config)
