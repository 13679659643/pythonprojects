# -*- coding: utf-8 -*-
# @Time    : 2024/8/9 17:25
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
from LogisticsDataFetcher_nextsls import LogisticsDataFetcher_nextsls

if __name__ == "__main__":
    # 创建 GesLogisticsDataFetcher 类的一个实例 fetcher
    fetcher = LogisticsDataFetcher_nextsls()
    # 调用 fetcher 的 run 方法开始执行数据抓取任务
    fetcher.run()