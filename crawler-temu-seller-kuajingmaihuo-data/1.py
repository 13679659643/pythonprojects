from datetime import datetime, timedelta

from base.crawler_base import CrawlerBase
from settings import orderlist_table_name

# print((datetime.now() - timedelta(days=7)).strftime('%Y%m%d'))
#
# a = 1734796800
# b = 1737561599
# from base.crawler_base import CrawlerBase
# print(CrawlerBase.timestr(a*1000))
# print(CrawlerBase.timestr(b*1000))
# now_date = datetime.now()
# startDate = (now_date - timedelta(days=31)).strftime('%Y-%m-%d 00:00:00')
# endDate = now_date.strftime('%Y-%m-%d 23:59:59')
# print(startDate)
# print(endDate)
# print(int(CrawlerBase.timestamp(startDate)/1000))
# print(int(CrawlerBase.timestamp(endDate)/1000))

CrawlerBase().get_mongodb_one_month(orderlist_table_name)