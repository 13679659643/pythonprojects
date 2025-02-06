# -*- coding: utf-8 -*-
# @Time    : 2025/1/9 16:42
# @Author  : Night
# @File    : crawler_kulu_expense_bill_management.py
# @Description:
import base64
import json
from datetime import datetime, timedelta
import requests
from loguru import logger
from crawler_base import BaseCrawler
from db_model import ods_scg_wld_kulu_expense_bill_management_i_d_field_list, \
    ods_scg_wld_kulu_expense_bill_management_table
from settings import fetcher_info


class KuluExpenseBillManagement(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.session = requests.session()
        self.now_date = datetime.now()
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.start_date = (self.now_date - timedelta(days=90)).strftime('%Y-%m-%d')
        self.data_list = []

    def init_logistic(self, logistics_provider: str):
        self.logistics_provider = fetcher_info[logistics_provider]['logistics_provider']
        self.logistics_provider_code = logistics_provider
        self.HASH_AUTH_TOKEN = fetcher_info[logistics_provider]['hash_token_path']
        self.key = fetcher_info[logistics_provider]['token_key']

    def btoa(self, s: str) -> str:
        # 将字符串编码为字节
        byte_data = s.encode('utf-8')
        # 使用base64进行编码
        base64_encoded_data = base64.b64encode(byte_data)
        # 将结果解码回字符串形式并返回
        return base64_encoded_data.decode('utf-8')

    def cost_type_map(self):
        """
        费用类型映射
        :return:
        """
        options = {
            "shipping": "运输费",
            "pay": "充值",
            "OPF": "操作费",
            "STC": "入库费",
            "CCF": "报关费",
            "TTS": "中转运输费",
            "WHF": "仓储费",
            "DLF": "提货费",
            "IN": "保险费",
            "other": "其他",
            "LLF": "超长费",
            "LLSC": "超长附加费",
            "LOC": "超长超大费",
            "ODA": "ODA",
            "CSF": "截单手续费",
            "ODAR": "偏远",
            "ODASR": "ODASR",
            "WHOSCOW": "仓储操作附加费按重量",
            "WHOSCOP": "仓储操作附加费按件数",
            "OTC": "单票费",
            "RDF": "住宅派送费",
            "FSC": "燃油附加费",
            "RSC": "偏远附加费",
            "RSF": "挂号费",
            "DT": "关税",
            "ACSC": "地址纠正附加费",
            "CUSCF": "清关费",
            "SKUCOST": "SKU成本",
            "CODEPRINT": "条码打印费",
            "package_fee": "包材费用",
            "DPCLF": "订单多品处理费",
            "DDCKF": "出库处理费",
            "package": "包材费",
            "diff_fee": "对帐差异费用",
            "OWS1": "超重费1",
            "OOF1": "超长超重费1",
            "OWS2": "超重费2",
            "OOF2": "超长超重费2",
            "UF": "超长超大拒收费",
            "pick_fee": "分拣费",
            "pallet_fee": "打托费",
            "shipment_fee": "出货费",
            "unload_fee": "卸货费",
            "package_code": "包材费",
            "labeling_fee": "贴标费",
            "check_fee": "清点费",
            "transfer_rent": "转运仓租"
        }
        return options

    def get_cost_bill_data(self, page: int = 1):
        """
        :param page: 页数
        :return:
        """
        data = {
            'E11': '',
            'writeOff': '',
            'E4': '',
            'orderSource': '',
            'is_upload': '',
            'business_code': '',
            'warehouse_id': '',
            'ft_code': '',
            'dateFor': '',
            'dateTo': '',
            'smId': '',
        }

        response = self.session.post(
            f'http://kulu.yunwms.com/fee/cost-bill/list/page/{page}/pageSize/500',
            data=data,
            verify=False,
        )
        if response.status_code == 200:
            return response.json()
        return None

    def etl_data(self, dataList):
        """
        列表数据
        :param dataList:
        :return:
        """
        cost_type_dict = self.cost_type_map()
        for row in dataList:
            row['dt'] = row['bi_chargeable_time'].split(" ")[0].replace("-", "")
            row['ft_code'] = cost_type_dict[row['ft_code']]
            self.data_list.append(row)

    def fetch_all_pages(self):
        """
        获取所有页面的数据
        """
        pageNo = 1
        while True:
            ret_data = self.get_cost_bill_data(pageNo)
            if not ret_data:
                break
            dataList = ret_data['data']
            total = int(ret_data['total'])
            page_total_ct = (total - 1) // 500 + 1
            self.etl_data(dataList)
            if pageNo >= page_total_ct:
                break
            pageNo += 1

    def login(self):
        with self.redis_client.conn as redis_conn:
            if not redis_conn.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                data = {
                    'userName': self.config[self.logistics_provider_code]['username'],
                    'userPass': self.btoa(self.config[self.logistics_provider_code]['password']),
                }

                response = self.session.post('http://kulu.yunwms.com/default/index/login',
                                             data=data, verify=False)
                if response.json()['message'] == 'Success':
                    set_cookies = dict(response.cookies)
                    redis_conn.hset(self.HASH_AUTH_TOKEN, self.key, json.dumps(set_cookies))
                    redis_conn.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 2 * 60 * 60, "1")
                    logger.info("酷麓海外仓-登录账号成功")
                else:
                    logger.warning(f"登录请求失败，状态码：{response.status_code}")

            return redis_conn.hget(self.HASH_AUTH_TOKEN, self.key)

    def init_headers(self, cookies):
        """
        更新账号登录cookie
        :param cookies:
        :return:
        """
        cookie_dict = json.loads(cookies.decode())
        self.session.cookies.update(cookie_dict)

    def insert_to_tidb(self):
        """
        存入到数据库中
        :return:
        """
        self.tidb.insert_data(ods_scg_wld_kulu_expense_bill_management_table,
                              ods_scg_wld_kulu_expense_bill_management_i_d_field_list,
                              self.data_list)
        logger.info(f'酷麓海外仓-费用账单管理数据同步{len(self.data_list)}完成')

    def main(self):
        self.init_logistic('KULU')
        kl_cookie = self.login()
        if not kl_cookie:
            return
        self.init_headers(kl_cookie)
        self.fetch_all_pages()
        self.insert_to_tidb()


if __name__ == '__main__':
    kulu = KuluExpenseBillManagement()
    kulu.main()
