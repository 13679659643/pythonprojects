# _*_ coding: utf-8 _*_
# @Time : 2024/8/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-lingxing-fba-shipmens
# @Desc :

import uvicorn
from fastapi import FastAPI, BackgroundTasks,HTTPException
from loguru import logger

from settings import PROJECT_ROUTE, PROJECT_TITLE, PostItems
from src.crawler.crawler_lx_fba_shipment_carton_detail import CrawlerLXFbaShipmentCartonDetail
from src.crawler.crawler_lx_shipment_kanban import LXShipmentKanban
from src.crawler.crawler_lx_shipment_kanban_item import LxShipmentKanbanItem

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
    return 'pong'


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
    operation_type = item.operation_type
    if sub_server == 'crawler_lx_fba_shipment_carton_detail':
        crawler = CrawlerLXFbaShipmentCartonDetail()
    elif sub_server == 'crawler_lx_shipment_kanban':
        crawler = LXShipmentKanban()
    elif sub_server == 'crawler_lx_shipment_kanban_item':
        crawler = LxShipmentKanbanItem()
    else:
        raise HTTPException(status_code=400, detail="Invalid service_name")

    if operation_type == 'sync':
        crawler.main()
    elif operation_type == 'async':
        background.add_task(crawler.main,)
    else:
        raise HTTPException(status_code=400, detail="Invalid operation_type")

if __name__ == '__main__':
    logger.info('准备开始')
    uvicorn.run(app, port=8000, host='0.0.0.0', log_config=log_config)
