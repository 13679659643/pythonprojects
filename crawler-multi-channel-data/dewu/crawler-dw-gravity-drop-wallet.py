# -*- coding: utf-8 -*-
# @Time    : 2024/12/12 11:08
# @Author  : Night
# @File    : crawler-dw-gravity-drop-wallet.py
# @Description:
import execjs
import requests
from base.crawler_base import CrawlerBase
from dewu import get_file_path
from dewu.db_model import ods_cd_sl_dw_gravity_drop_wallet_db_table, \
    ods_cd_sl_dw_gravity_drop_wallet_i_d_field_list
from settings import RedisKeys
from loguru import logger
import pandas as pd


class CrawlerDwGravityDropWallet(CrawlerBase):
    def __init__(self):
        super().__init__()
        self.sensor_cookies = {
            'sensorsdata2015jssdkcross': '',
        }
        self.data_list = []
        self.gravity_authorization = ''

    def get_sign(self, params):
        """
        加密sign
        """
        with open(get_file_path('sign.js'), 'r', encoding='utf-8') as fp:
            jsdata = fp.read()
        ctx = execjs.compile(jsdata)
        sign = ctx.call('biz_sign', params)
        return sign

    def gravity_platform_login(self):
        """
        得物引力 登录
        """
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://gravity.dewu.com',
            'Pragma': 'no-cache',
            'Referer': 'https://gravity.dewu.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'X-Merc-SysCode': 'DEWU_MERCHANT_PLATFORM_DU_USER_T',
            'X-Merc-Token': self.cookies,
            'appVersion': '5.56.0',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-xdw-video-flag': 'true',
        }
        params = {}
        json_data = {
            'type': 1,
        }
        params['sign'] = self.get_sign(json_data)
        response = requests.post('https://app.dewu.com/sns-bom/v1/common/platform/login', params=params,
                                 headers=headers, json=json_data)
        if response.status_code == 200:
            return response.json()['data']['token']
        return None

    def get_file_export_token(self, start_time, end_time):
        """
        获取文件下载token
        """
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Authorization': self.gravity_authorization,
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://gravity.dewu.com',
            'Pragma': 'no-cache',
            'Referer': 'https://gravity.dewu.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            'X-Merc-SysCode': 'DEWU_MERCHANT_PLATFORM_DU_USER_T',
            'appVersion': '5.56.0',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'x-xdw-video-flag': 'true',
        }
        params = {}
        json_data = {
            'startTime': start_time,
            'endTime': end_time,
            'scene': 6,
            'bizArea': 'gravity',
        }
        params['sign'] = self.get_sign(json_data)
        response = requests.post(
            'https://app.dewu.com/sns-bom/v1/common/platform/file/export',
            params=params,
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            return response.json()['data']['exportToken']
        return None

    def get_file_export_url(self, export_token):
        """
        获取文件下载地址
        """
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Authorization': self.gravity_authorization,
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://gravity.dewu.com',
            'Pragma': 'no-cache',
            'Referer': 'https://gravity.dewu.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'X-Merc-SysCode': 'DEWU_MERCHANT_PLATFORM_DU_USER_T',
            'appVersion': '5.56.0',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-xdw-video-flag': 'true',
        }
        params = {}
        json_data = {
            'scene': 6,
            'bizArea': 'gravity',
            'exportToken': export_token,
        }
        params['sign'] = self.get_sign(json_data)
        response = requests.post(
            'https://app.dewu.com/sns-bom/v1/common/platform/file/export-result',
            params=params,
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            return response.json()['data']['exportUrl']
        return None

    def download_file(self, account, export_url):
        """
        下载链接数据
        """
        df = pd.read_excel(export_url)
        df = df.fillna('')
        for index, row in df.iterrows():
            processed_dict = self.etl_data(row)
            processed_dict['dt'] = processed_dict['order_time'].split(" ")[0].replace("-", "")
            processed_dict['account'] = account
            self.data_list.append(processed_dict)

    def del_data(self, account, start_date, end_date):
        """
        删除数据
        """
        sql = f"delete from ods_prod.ods_cd_sl_dw_gravity_drop_wallet_i_d where dt>={start_date.replace('-', '')} and dt<={end_date.replace('-', '')}"
        self.tidb.commit_sql(sql)
        logger.info(f"删除 得物-营销-引力投放 {account} {start_date}至{end_date} 数据")

    def etl_data(self, row: pd.Series):
        """
        处理数据
        :param data:
        :return:
        """
        processed_data = {
            'parent_id': row.iloc[0],  # 父任务id
            'sub_id': row.iloc[1],  # 子任务id
            'heating_name': row.iloc[2],  # 加热名称
            'order_time': row.iloc[3],  # 下单时间
            'amt_transfer_time': row.iloc[4],  # 金额流转时间
            'transaction_status': row.iloc[5],  # 交易状态
            'transaction_amt': row.iloc[6],  # 交易金额
            'task_type': row.iloc[7],  # 任务类型
        }
        return processed_data

    def main(self):
        user_infos = self.tidb.get_user_info('DW')
        for dw_info in user_infos:
            account = dw_info['account']
            self.init_user_cookies(RedisKeys.DW_STARK_LOGIN_KEY.value, account)
            self.gravity_authorization = self.gravity_platform_login()
            if self.gravity_authorization is None:
                logger.error(f'得物-用户:{account} 引力投放授权失败')
                continue
            # 最多导出90天数据
            start_time, end_time = self.get_time_range(in_day=61)
            # 删除数据
            self.del_data(account, start_time, end_time)
            exportToken = self.get_file_export_token(start_time, end_time)
            # 获取导出的url
            export_url = self.get_file_export_url(exportToken)
            # 通过url链接下载数据
            self.download_file(account, export_url)
            self.save_to_tidb(ods_cd_sl_dw_gravity_drop_wallet_db_table,
                              ods_cd_sl_dw_gravity_drop_wallet_i_d_field_list, self.data_list)
            logger.info(f'得物-营销-引力投放 {account} {len(self.data_list)} 采集完成')
            self.data_list.clear()


if __name__ == "__main__":
    crawler = CrawlerDwGravityDropWallet()
    crawler.main()
