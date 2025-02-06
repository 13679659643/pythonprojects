# -*- coding: utf-8 -*-
# @Time    : 2023/11/15 14:16
# @Author  : night
# @Email   :
# @File    : 
# @Software:
import uvicorn
from digiCore.model import PostItems, WebEnum, ItemEnum
from fastapi import FastAPI, BackgroundTasks, APIRouter
from loguru import logger

from crawler_lx_platform_fbc_stock import CrawlerPlatformFbcStock
from crawler_lx_platform_wfs_stock import CrawlerPlatformWfsStock
from mp_platform_wh_shipment import MpPlatformWHShipment
from mp_platform_wh_shipment_detail import MpPlatformWHShipmentDetail
from settings import prefix, PROJECT_TITLE
from digiCore.utils import MsgTool

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
    return MsgTool.format_api_msg(WebEnum.STATUS_SUCCESS)


@PROJECT_ROUTE.post("/stock")
async def sync_start(item: PostItems, background: BackgroundTasks):
    """
    同步多平台库存
    """
    # 子服务名称 必须与 py程序名称一致。
    sub_server = item.subserver
    operation_type = item.operation_type
    if sub_server == 'crawler_lx_platform_fbc_stock':
        sapr = CrawlerPlatformFbcStock()
    elif sub_server == 'crawler_lx_platform_wfs_stock':
        sapr = CrawlerPlatformWfsStock()
    else:
        return f"子服务名称错误，实例化失败！--{sub_server}"

    # 异步启动程序
    if operation_type == ItemEnum.OPERATION_ASYNC:
        background.add_task(sapr.main, )
        logger.info("程序异步启动成功！")
        return MsgTool.format_api_msg(WebEnum.STATUS_SUCCESS)
    else:
        logger.info("程序同步启动成功！等待程序执行完成")
        sapr.main()
        logger.info("程序同步执行完成！")
        return MsgTool.format_api_msg(WebEnum.STATUS_SUCCESS)


@PROJECT_ROUTE.post("/wh_shipment")
async def sync_start(item: PostItems, background: BackgroundTasks):
    """
    同步多平台发货单数据
    :param background:
    :return:
    """
    # 子服务名称 必须与 py程序名称一致。
    sub_server = item.subserver
    operation_type = item.operation_type
    if sub_server == 'mp_platform_wh_shipment':
        sapr = MpPlatformWHShipment()
    elif sub_server == 'mp_platform_wh_shipment_detail':
        sapr = MpPlatformWHShipmentDetail()
    else:
        return f"子服务名称错误，实例化失败！--{sub_server}"
    # 异步启动程序
    if operation_type == ItemEnum.OPERATION_ASYNC:
        background.add_task(sapr.main, )
        logger.info("程序异步启动成功！")
        return MsgTool.format_api_msg(WebEnum.STATUS_SUCCESS)
    else:
        logger.info("程序同步启动成功！等待程序执行完成")
        sapr.main()
        logger.info("程序同步执行完成！")
        return MsgTool.format_api_msg(WebEnum.STATUS_SUCCESS)


if __name__ == '__main__':
    logger.info('准备开始')
    app.include_router(PROJECT_ROUTE)
    uvicorn.run(app, port=8000, host='0.0.0.0', log_config=log_config)
