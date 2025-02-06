import json
from datetime import timedelta, datetime
from loguru import logger
from jd_jm import get_file_path
from db._redis import RedisClient
from db._tidb import TidbConnector
import execjs
import requests

from jd_jm.db_model import ods_cd_sl_jd_jm_refundamt_i_d_field_list, ods_cd_sl_jd_jm_refundamt_db_table
from method.crawler_base import BaseCrawler
from settings import RedisKeys


class fetcher_jd_jm_refundamt:
    """
    京麦-自主售后-退款金额数据
    """
    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.now_date = datetime.now()
        self.startDate = (self.now_date - timedelta(days=31)).strftime('%Y-%m-%d 00:00:00')
        self.endDate = self.now_date.strftime('%Y-%m-%d 23:59:59')
        self.data_list = []
        self.cookies = {}
        self.account = ''

    def get_cookies(self):
        redis_key = f"{RedisKeys.JD_JM_LOGIN_KEY.value}:{self.account}"
        jm_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not jm_cookie:
            logger.info(f"京麦 {self.account} cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        jm_cookie_dict = json.loads(jm_cookie)
        return jm_cookie_dict

    def fetch_page_data(self, page=1):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""
        headers = {
            'authority': 'sff.jd.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'dsm-file-path': 'lineation-price',
            'dsm-lang': 'zh-CN',
            'dsm-platform': 'pc',
            'dsm-site': '',
            'dsm-trace-id': '53c7a655-4750-4e82-8e0c-74c6bcaa23c1',
            'origin': 'https://shop.jd.com',
            'pragma': 'no-cache',
            'referer': 'https://shop.jd.com/jdm/trade/after-sale/independent-after-sale/list?tabCode=waitAudit',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        # 京麦-自主售后-退款金额数据
        params = {
            'v': '1.0',
            'appId': 'BHPQ4MHJBUOQZKTFTRNS',
            'api': 'dsm.seller.afs.serviceOrderQueryDsmService.page',
        }
        json_data = {
            'request': {
                'data': {
                    'tabCode': 'all',
                    'pageIndex': page,
                    'pageSize': 100,
                    # 'customerExpectList': [
                    #     10,
                    # ],
                    'applyTimeRange': {
                        'dateBegin': BaseCrawler.timestamp(self.startDate),
                        'dateEnd': BaseCrawler.timestamp(self.endDate),
                    },
                },
            },
        }
        response = requests.post('https://sff.jd.com/api', params=params, cookies=self.cookies, headers=headers, json=json_data)
        if response.status_code != 200:
            return {}
        # response = response.json()
        # lena = len(response['data']['content'])
        # print(json.dumps(response))
        # print(lena)
        # exit()
        return response.json()

    def fetch_all_data(self, data_dict: dict):
        """顺序获取所有页的数据"""
        if not data_dict:
            return []
        elif data_dict['data']['totalNum'] == '0':
            logger.info(f"朗盟京麦-自主售后-退款金额数据 交易明细页面无数据")
            return []
        # 获取总行数（total_rows）和每页的大小（page_size）
        total_rows = data_dict['data']['totalNum']
        page_size = 100
        # 将总行数加上每页大小减一,然后整除每页大小来完成的.这样做是为了确保如果总行数不能被每页大小整除时,总页数会向上取整.
        total_pages = (int(total_rows) + page_size - 1) // page_size
        total_page_data = []
        for page in range(1, total_pages + 1):
            try:
                page_data = self.fetch_page_data(page)
                total_page_data.append(page_data)
            except Exception as e:
                logger.error(f'------- 任务执行中发生了异常: {e} -------')
        return total_page_data

    def process_data(self, total_page_data: list[dict]):
        """处理每页的数据"""
        processed_data_all = []
        for page_data in total_page_data:
            page_dataSource = page_data['data']['content']
            for item in page_dataSource:
                try:
                    afsServiceId = item.get('relationFacetDTO').get('afsServiceId')
                    orderId = item.get('relationFacetDTO').get('orderId')
                    afsApplyTime = BaseCrawler.timestr(item.get('serviceOrderBaseFacetDTO').get('afsApplyTime'))
                    dt = BaseCrawler.date_str(afsApplyTime)

                    refundFacetDTO = item.get('refundFacetDTO')
                    if refundFacetDTO.get('refundAmount') is not None:
                        refundAmount = refundFacetDTO.get('refundAmount')
                        refundStatusName = refundFacetDTO.get('refundStatusName')
                    else:
                        refundAmount = 'None'
                        refundStatusName = 'None'

                    customerExpectName = item.get('customerExceptFacetDTO').get('customerExpectName')
                    afsReasons = item.get('customerApplyFacetDTO').get('applyReasonFacetDTO').get('afsReasons')
                    serviceOrderSubStateName = item.get('serviceOrderStatusFacetDTO').get('serviceOrderSubStateName')

                    # 使用列表推导式获取 "主商品" 的 wareNum
                    main_product_nums = [info['wareNum'] for info in item.get('wareFacetDTOList') if
                                         info['wareTypeName'] == '主商品']

                    # 使用 sum 函数计算总和
                    wareNum = sum(main_product_nums)

                    row_dict = {
                        "account": self.account,
                        "afsServiceId": afsServiceId,
                        "orderId": orderId,
                        "afsApplyTime": afsApplyTime,
                        "dt": dt,
                        "refundAmount": refundAmount,
                        "wareNum": wareNum,
                        "refundStatusName": refundStatusName,
                        "customerExpectName": customerExpectName,
                        "afsReasons": afsReasons,
                        "serviceOrderSubStateName": serviceOrderSubStateName
                    }
                    processed_data_all.append(row_dict)
                except Exception as e:
                    logger.warning(f"处理数据Error: {e}")
        self.data_list.extend(processed_data_all)

    def get_jd_jm_data(self):
        self.tidb.insert_data(ods_cd_sl_jd_jm_refundamt_db_table, ods_cd_sl_jd_jm_refundamt_i_d_field_list,
                              self.data_list)
        logger.info(f"朗盟京麦-自主售后-退款金额数据 时间：{self.startDate} ~ {self.endDate} 同步 {len(self.data_list)} 完成")

    def main(self):
        # [dist]
        jd_JM_user_infos = self.tidb.get_user_info('JD-JM')
        for jd_jm_info in jd_JM_user_infos:
            self.account = jd_jm_info['account']
            self.cookies = self.get_cookies()
            if self.cookies is None:
                continue
            data_dict = self.fetch_page_data()
            total_page_data = self.fetch_all_data(data_dict)
            self.process_data(total_page_data)
        self.get_jd_jm_data()



if __name__ == "__main__":
    fetcher = fetcher_jd_jm_refundamt()
    fetcher.main()
