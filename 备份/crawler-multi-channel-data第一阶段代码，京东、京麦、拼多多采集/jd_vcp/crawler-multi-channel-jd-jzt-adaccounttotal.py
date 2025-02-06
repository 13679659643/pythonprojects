import json
import random
import time
from datetime import datetime, timedelta

import execjs
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from jd_vcp.db_model import ods_cd_sl_jd_jzt_adaccounttotal_db_table, ods_cd_sl_jd_jzt_adaccounttotal_i_d_field_list
from method.crawler_base import BaseCrawler
from settings import RedisKeys
from pprint import pprint


class fetcher_jd_jzt_adaccounttotal:
    """
    京准通--搜推广告概况--账户汇总!
    """

    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.Date = ''
        self.account = ''
        self.data_list = []
        self.cookies = ''

    def get_cookies(self):
        redis_key = f"{RedisKeys.JD_LOGIN_KEY.value}:{self.account}"
        jd_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not jd_cookie:
            logger.info(f"京东自营京准通--搜推广告概况--账户汇总 cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        jd_cookie_dict = json.loads(jd_cookie)
        return jd_cookie_dict

    def fetch_page_data(self):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""
        headers = {
            'authority': 'atoms-api.jd.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'shshshfpa=4d87f2c7-3edc-da1b-822c-0c0de9af27bd-1679036360; shshshfpx=4d87f2c7-3edc-da1b-822c-0c0de9af27bd-1679036360; __jdv=56585130|direct|-|none|-|1732518335885; __jdu=17325183358842067120209; language=zh_CN; style_flag=vcStyle; _ga_2TQ4PLYBNK=GS1.1.1732693791.1.0.1732693791.60.0.0; _ga=GA1.2.2146812876.1732693792; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221936c9914a4abc-0f34ebdc89f8a2-26001851-3688960-1936c9914a51e2b%22%2C%22%24device_id%22%3A%221936c9914a4abc-0f34ebdc89f8a2-26001851-3688960-1936c9914a51e2b%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; is_sz_old_version=false; b_belong=XWMCOEOLJD37J5GS2RT7LWCKUO7G67227B5DATCGB6JAT4QJVBRXU276EQYKZ3L67FGDS5XCG5JYNPURJMH7JNYIRJYOXL66W672HZL3EA467STZ6X3HQTON44WMGG46Q5U65IMIAR6VPXA2BIJADEUGPK63SRDFTUTKGRY; __USE_NEW_PAGEFRAME__=true; __USE_NEW_PAGEFRAME_VERSION__=v11; user-key=184f2369-53ab-4b4a-98b8-84d86fd45166; cn=6; shshshfpb=BApXSWBIBdPZAcVzXzJs0rzDlZXpSaZZnBztCZE9X9xJ1Mis8iIO2; hf_time=1732886932865; _base_=YKH2KDFHMOZBLCUV7NSRBWQUJPBI7JIMU5R3EFJ5UDHJ5LCU7R2NILKK5UJ6GLA2RGYT464UKXAI4Z6HPCTN4UQM3WHVQ4ENFP57OCY6B4XHNS3F5CPF7UULTFXVJKY2WAFHNI4XONTCAYDFTEPMP62QNNZELA6E4S4L2GLWBLTAIW5N6ZGEONMNNA5DQRDPVL52KNRE2QP7P6G3RICAAIPB6AG4MEKLVTSGRNHHLR3PX2TFCLHETNGQGVNGCPAES2GR7OYV5UOBAU2QYI5TB5CSMBPGJLU3IIOAKGMN6OBEN52BXQE4THMDAVPH6DN26O4DFUXS7FUBSEJDEFUIYLS62HE5HO3Q5WH3PJG5WNBQR6MS4CQZXWPNJTFGL7XH; wlfstk_smdl=iedalm6g3bbaa4wbx1lfysobjoe2x4ag; 3AB9D23F7A4B3C9B=CLZHCCN65TAV32BQGX5DBM6LHTJJWUENYT6YSNC2Z37G4KTEYJG5RAOMJPT3MNGVMUMDS3UIU5GAWV2TKFPJV3W4WQ; pinId=ZwaEaYCGZB9A9AXplivx1A; pin=DOOCN2017; unick=p85b1fnqr19fj0; ceshi3.com=000; _tp=eKY%2BJjLoFkNb4ZRjrAJW2Q%3D%3D; logining=1; _pst=DOOCN2017; VC_INTEGRATION_JSESSIONID=f2445127-a998-4fc0-a736-b6f1ea48a448; 3AB9D23F7A4B3CSS=jdd03CLZHCCN65TAV32BQGX5DBM6LHTJJWUENYT6YSNC2Z37G4KTEYJG5RAOMJPT3MNGVMUMDS3UIU5GAWV2TKFPJV3W4WQAAAAMTPP2BG4YAAAAADM7NZUD4JHV7LMX; TrackID=17dXZcIwZZ1zAtyJxauwQO9JuLAZjF1A16AF3vfAJSf8e31eDJZawVhfwszRUSy2J2YZupaNWFn7HpLWnaxpyYk0O_0C-Iz08xYTnhaomwM0; thor=C7BFD122C8A48B9163EC355D6751DDD3CECA211585B2073DF3E28B8B654CFDF52A6327E75E7A28DFCADC4AD62480628CFE408B64C00CEA39324D9021223B3191759165803F84ECDAE4D32FC7FA82EF13A45DAF8955150BBE28EAA7D60C4BB8A4141778EDC67F82F533CB6D2786F05A1E78B5001C599E41F786CDCA2FB584EFAB074E8238C06C9A293BC9B8E9A43FAEDD; flash=3_iWiiHLr2Fs5_lpgn8Mgtksx-UCavgg1m4aVBZCdn0fImA-d-VkVcxrn0SnGXfgOUNIL_WMbAA_AKe0Idba6Pg_bBqnPh6gfwFoJzn6yqFnLCdLyXto2y-rCG1T8GBDA4-RZ9QipCr1PZnJnjzh5dXK7CRlZZ0R_KuSGqRl49v2q*; light_key=AASBKE7rOxgWQziEhC_QY6yaY2I-vmia1KR0K03NIWRxGB56gO3PHehNZRmAlxhApSWotvtP; cn_language=zh_CN; atoms_router=749aea019f093991251c381dfa0f1b74; jbm_language=zh_CN; __jdc=146207855; __jda=146207855.17325183358842067120209.1732518336.1733118562.1733126944.12; __jdb=146207855.1.17325183358842067120209|12.1733126944',
            'language': 'zh_CN',
            'loginmode': '0',
            'origin': 'https://jzt.jd.com',
            'referer': 'https://jzt.jd.com/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'siteid': '0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        json_data = {
            'startDay': f'{self.Date} 00:00:00',
            'endDay': f'{self.Date} 23:59:59',
            'businessType': -1,
            'mediaResourceType': None,
            'interactiveType': None,
            'clickOrOrderDay': 15,
            'clickOrOrderCaliber': 0,
            'orderStatusCategory': None,
            'giftFlag': 0,
        }

        response = requests.post('https://atoms-api.jd.com/reweb/common/indicator', cookies=self.cookies,
                                 headers=headers,
                                 json=json_data)
        # 执行某些操作之间引入随机的延迟，以模拟人类行为或减轻对服务器的压力。choice:元素;choices:列表;
        time.sleep(random.choice([0.2, 0.4, 0.6]))
        if response.status_code != 200:
            return {}
        # json.dumps() 是 Python json 模块的一个函数，它将 Python 对象转换（序列化）为 JSON 格式的字符串。
        return response.json()

    def process_data(self, page_data: dict):
        """处理每天的数据"""
        try:
            page_data = page_data['data']
            page_data['dt'] = self.Date
        except Exception as e:
            logger.warning(f"京东自营京准通--搜推广告概况--账户汇总 {self.Date} {self.account} 处理数据Error: {e}")
            return
        self.data_list.append(page_data)

    def get_jd_jzt_data(self):
        self.tidb.insert_data(ods_cd_sl_jd_jzt_adaccounttotal_db_table, ods_cd_sl_jd_jzt_adaccounttotal_i_d_field_list,
                              self.data_list)
        logger.info(f"京东自营京准通--搜推广告概况--账户汇总 当前时间：{self.Date} {self.account} 同步 {len(self.data_list)} 完成")

    def main(self):
        jd_user_infos = self.tidb.get_user_info('JD')
        for jd_info in jd_user_infos:
            self.account = jd_info['account']
            self.cookies = self.get_cookies()
            if self.cookies is None:
                continue
            dates = BaseCrawler.generate_date_list()
            for date in dates:
                self.Date = date
                data_dict = self.fetch_page_data()
                self.process_data(data_dict)
        self.get_jd_jzt_data()


if __name__ == "__main__":
    fetcher = fetcher_jd_jzt_adaccounttotal()
    fetcher.main()
