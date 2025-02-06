# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import requests
from loguru import logger
from base.crawler_base import CrawlerBase, RetryDecorator
from data_pipeline.mongo_tidb_transfer_salesact_thematicact import MongoTidbTransferShort
from db_model import ods_cd_sl_temu_seller_thematicact_i_d_db_table, ods_cd_sl_temu_seller_thematicact_i_d_field_list
from settings import db_name, mg_thematicact_field_list, thematicact_table_name
from login.temu_login import AuthTemuLogin


class CrawlerTemuCentralSalesActShort(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.data_list = []
        self.mallId = ''
        self.mallName = ''
        self.table_ob=self.mongo_ob.load_table_ob(db_name, thematicact_table_name)

    @RetryDecorator.retry(max_attempts=2)
    def get_productlist(self, pageNo: int = 1):
        """
        temu-跨境卖家中心-店铺营销-营销活动-专题活动
        """
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'anti-content': '0aqAfqnygcKgjgd9n0fogbzhoP67evx-btepqApwgOZkw9GcpBkEIODMzeAf1QXf3MN8g324BPxPnVh5cjz4YvtDvjfaPzbXKUTGK_zE1QIaHKKs915ho2YPJLzq-hmqrJJWA306KI5Sxx3VlDwjtxBjDORXFcKe_cnHpgYL97bZMSwIR961F-oVroXsHy6WMQAyDvBMHH1Dutoa0oA77Hi1rWT0UU-SdeWa0JM6HHuDfiJ6N82vkkt6KGWl3ew0zxyQgvjN4zb9_L4SN4rE9cOKzvd8Eerywtk9xcK9v72p7Zx07aGjO67b0Hb6na2vN90m2BOogip4RjRO0J1x5RSEAtprz9W9hiI3dTbF5gF7YY0NyvOBnUZm5d-IjhkIA5eFO8-Dfn7dF_CHZl7nxdSZaFdC7i_ZIjw7bNuWwa16YNbnn9-ZFR63G9V5fPTLVFPV-NX_dsf49m-zwT457fFnsIpixv7uahA5wc0iIwhB9KomaGHBigcjwboOosZvZTbKeAsw00Tqybg9ijOnfNJN9VABiTfGyOZpVIqoOB2bk6Y1jZ0Y8686gr-rBb8-SsOgCl5f6f4ArsffkybRhNcej7cDLJOBN8D2doz74coeI84AOzt7DomSbVrfudq__Pa35EhfzvXG-DRhJnBCluSsUgZ2hkGlOsR_soYSpgYBqmikO58nQoIA6C_MdxA5B1iWENLSJ-ME3Cva8od0a3fCLzv_UlUC',
            'cache-control': 'max-age=0',
            'content-type': 'application/json',
            # 'cookie': 'api_uid=CmjNt2d7ongoZwBSrzSOAg==; _nano_fp=Xpmqn5gynpmjnqdYnC_VBPNrudnmtP4byPRS5etQ; _bee=ktb70a57iYsSvZD6v0fiMNcIdMB5namH; _f77=d07249cd-10e9-4fd4-bfad-8ecce7cb689e; _a42=e7b848d3-0f95-4c52-be12-f523847513c5; rckk=ktb70a57iYsSvZD6v0fiMNcIdMB5namH; ru1k=d07249cd-10e9-4fd4-bfad-8ecce7cb689e; ru2k=e7b848d3-0f95-4c52-be12-f523847513c5; SUB_PASS_ID=eyJ0IjoiZ0xWY2lwZkZnSlkyQXZVTmRFbk9RZkRCakZqV0IrY1YxaGgvbnFhVDZ1UnkrTVdCakNNMkQ5T1ZQVE9SaXhidyIsInYiOjEsInMiOjEwMDAwLCJ1IjoyMTkzNzMxNjMzMzA5NH0=',
            'mallid': self.mallId,
            'origin': 'https://seller.kuajingmaihuo.com',
            'priority': 'u=1, i',
            'referer': 'https://seller.kuajingmaihuo.com/activity/marketing-activity/log',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        }

        json_data = {
            'pageNo': pageNo,
            'pageSize': 40,
        }

        response = requests.post(
            'https://seller.kuajingmaihuo.com/marvel-mms/cn/api/kiana/gambit/marketing/activity/product/applied/list',
            cookies=self.cookies,
            headers=headers,
            json=json_data,
        )
        if response.json()['result'] is None:
            logger.info(response.json())
            return None
        if response.status_code == 200:
            return response.json()
        return None

    def fetch_all_pages(self,):
        """
        获取所有页面的数据
        """
        page_ct = 1
        has_more = True
        while has_more:
            ret_data = self.get_productlist(page_ct)
            if ret_data['result']['productList'] is None:
                break
            total = ret_data['result']['total']
            data_list = ret_data['result']['productList']
            result = CrawlerBase().add_fields(data_list, 'mallId', self.mallId, 'mallName', self.mallName)
            page_total_ct = (total - 1) // 40 + 1
            self.data_list.extend(result)
            has_more = page_ct < page_total_ct
            page_ct += 1

    @RetryDecorator.retry_decorator()
    def run(self, account: str, password: str):
        """
        流程主体
        :return:
        """
        temulogin = AuthTemuLogin(account, password)
        self.cookies = temulogin.main()
        if not self.cookies:
            return
        UserInfo = self.userInfo()
        mall_info_list = CrawlerBase().mallId(UserInfo)
        for userinfo in mall_info_list:
            self.mallId = str(userinfo['mallId'])
            self.mallName = userinfo['mallName']
            self.fetch_all_pages()
            self.mongo_ob.bulk_save_data(self.data_list, mg_thematicact_field_list, self.table_ob)
            logger.info(
                f'temu-跨境卖家中心-店铺营销-营销活动-专题活动 {account} {self.mallName} {len(self.data_list)} 存入mongo完成')
            self.data_list.clear()  # 清空列表 list

    def main(self):
        user_infos = self.tidb.get_user_info('TEMU')
        for temu_info in user_infos:
            account = temu_info['account']
            # if account == '13074832078':
            password = temu_info['password']
            self.run(account, password)
        thematicact_list = MongoTidbTransferShort().etl_data()
        self.save_to_tidb(ods_cd_sl_temu_seller_thematicact_i_d_db_table,
                          ods_cd_sl_temu_seller_thematicact_i_d_field_list, thematicact_list)
        logger.info(f'temu-跨境卖家中心-店铺营销-营销活动-专题活动 {len(thematicact_list)} 条数据采集完成')



if __name__ == "__main__":
    crawler = CrawlerTemuCentralSalesActShort()
    crawler.main()
