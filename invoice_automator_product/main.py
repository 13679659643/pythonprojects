# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 15:35
# @Author  : Night
# @File    : settings.py
# @Description:

import uvicorn
from fastapi import FastAPI, APIRouter, BackgroundTasks
from loguru import logger
from digiCore.db.redis.core import RedisDao
from utils.tool import md5_encrypt

from settings import redis_crawler_run_sign
from settings import prefix, PROJECT_TITLE
from src.invoice_generation import InvoiceGeneration

app = FastAPI(docs_url=f'{prefix}/docs',
              redoc_url=f'{prefix}/redoc',
              openapi_url=f'{prefix}/openapi.json', title=PROJECT_TITLE, )

# 接口蓝图
PROJECT_ROUTE = APIRouter(prefix=prefix)
log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"


# 1、同步宜搭表单数据接口
# 2、执行指定监控服务接口
@PROJECT_ROUTE.get("/fba")
async def sync_product_fba(back_task: BackgroundTasks, shipment_id, amz_code):
    """
    :param back_task:
    :param shipment_id: FBA发货单号
    :param amz_code: 亚马逊追踪编码
    :return:
    """
    redis_client = RedisDao()
    md5_cant_str = shipment_id + amz_code
    md5_fmt = md5_encrypt(md5_cant_str)
    redis_run_sign = redis_crawler_run_sign.format(md5_fmt)
    if redis_client.setnx_run_sign(redis_run_sign):
        c = InvoiceGeneration(
            shipment_id=shipment_id,
            amz_code=amz_code,
            redis_run_sign=redis_run_sign
        )
        back_task.add_task(c.main, )
        logger.info(f"同步程序开始！{shipment_id}")
        return "同步程序开始！"
    return "程序已经启动成功，无需重复点击！"


if __name__ == '__main__':
    logger.info('准备开始')
    app.include_router(PROJECT_ROUTE)
    uvicorn.run(app, port=8000, host='0.0.0.0', log_config=log_config)
