# -*- coding: utf-8 -*-
# @Time    : 2023/09/04
# @Author  : night
# @Email   :
# @File    :
# @Software:

from digiCore.utils import DateTool
from loguru import logger

from common_resources import CrawlerBase
import concurrent.futures

from crawler_lx_profit_statement_base import StatementProducerCrawler, StatementConsumerCrawler
class CrawlerProfitStatementData(CrawlerBase):

    def main(self):
        """
        启动程序
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            # 生产者
            p = StatementProducerCrawler()
            # 消费者
            c = StatementConsumerCrawler()
            days = self.extra_params.get('days', 14)
            start_date, end_date = DateTool.get_task_date(days)
            date_list = DateTool.get_date_list(start_date, end_date, date_format="%Y-%m-%d")
            for date in date_list:
                p.produce(date)
                futures = [executor.submit(c.consume, ) for _ in range(10)]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f'任务执行中发生了异常: {e}')
                c.save_data()


if __name__ == '__main__':
    sapr = CrawlerProfitStatementData()
    sapr.extra_params = {'days': 15}
    sapr.main()
