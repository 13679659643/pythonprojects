import json
from datetime import datetime, timedelta
import requests
from loguru import logger
from db._redis import RedisClient
from db._tidb import TidbConnector
from jd_vcp.db_model import ods_cd_sl_jd_fc_solidsales_db_table, ods_cd_sl_jd_fc_solidsales_i_d_field_list
from settings import RedisKeys
from pprint import pprint


class fetcher_jd_fc_solidsales:
    """
    京东自营--财务管理--结算管理--实销实结明细
    """
    def __init__(self):
        self.tidb = TidbConnector()
        self.redis_client = RedisClient().redis_client()
        self.now_date = datetime.now()
        self.startDate =(self.now_date - timedelta(days=7)).strftime('%Y-%m-%d')
        self.endDate =self.now_date.strftime('%Y-%m-%d')
        self.account= ''
        self.cookies = ''

    def get_cookies(self):
        redis_key = f"{RedisKeys.JD_LOGIN_KEY.value}:{self.account}"
        jd_cookie = self.redis_client.get_auth_cookie(redis_key)
        if not jd_cookie:
            logger.info(f"京东自营--财务管理--结算管理--实销实结明细 cookie已失效")
            # 输出：None
            return
        # 用于将一个 JSON 格式的字符串转化为 Python 对象。
        jd_cookie_dict = json.loads(jd_cookie)
        return jd_cookie_dict

    def fetch_page_data(self, page=1, ):
        """获取指定tab的page页的数据，page=1，没有传参时默认为一，位置必须在最后"""
        headers = {
            'authority': 'vcf.jd.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json;charset=UTF-8',
            # 'cookie': 'shshshfpa=4d87f2c7-3edc-da1b-822c-0c0de9af27bd-1679036360; shshshfpx=4d87f2c7-3edc-da1b-822c-0c0de9af27bd-1679036360; __jdv=56585130|direct|-|none|-|1732518335885; __jdu=17325183358842067120209; language=zh_CN; style_flag=vcStyle; _ga_2TQ4PLYBNK=GS1.1.1732693791.1.0.1732693791.60.0.0; _ga=GA1.2.2146812876.1732693792; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221936c9914a4abc-0f34ebdc89f8a2-26001851-3688960-1936c9914a51e2b%22%2C%22%24device_id%22%3A%221936c9914a4abc-0f34ebdc89f8a2-26001851-3688960-1936c9914a51e2b%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; is_sz_old_version=false; user-key=184f2369-53ab-4b4a-98b8-84d86fd45166; cn=6; shshshfpb=BApXSWBIBdPZAcVzXzJs0rzDlZXpSaZZnBztCZE9X9xJ1Mis8iIO2; hf_time=1732886932865; wlfstk_smdl=iedalm6g3bbaa4wbx1lfysobjoe2x4ag; pinId=ZwaEaYCGZB9A9AXplivx1A; ceshi3.com=000; _tp=eKY%2BJjLoFkNb4ZRjrAJW2Q%3D%3D; _pst=DOOCN2017; cn_language=zh_CN; jbm_language=zh_CN; 3AB9D23F7A4B3C9B=CLZHCCN65TAV32BQGX5DBM6LHTJJWUENYT6YSNC2Z37G4KTEYJG5RAOMJPT3MNGVMUMDS3UIU5GAWV2TKFPJV3W4WQ; 3AB9D23F7A4B3CSS=jdd03CLZHCCN65TAV32BQGX5DBM6LHTJJWUENYT6YSNC2Z37G4KTEYJG5RAOMJPT3MNGVMUMDS3UIU5GAWV2TKFPJV3W4WQAAAAMTROGPZ4AAAAAADSEUBJZR7I34ZIX; TrackID=1qVl7QwEvqBokkDuOtEX5CQK361vL-TMqSCv14sbP2VeUSSF2swFPIyP7jrHnTC7aUCz-VZRs5i5rBawzp5Iy382ylqvdc2xEkN_tCj-lVzo; thor=C7BFD122C8A48B9163EC355D6751DDD3F6C1D776F02EA79443F04272C6DE4B1502BBD1D1C52AB7E5A209F862E01685DE12FE513F1526FC265B03F7F30FCE7B715E1A04893FBACF36722D4C8854B33812C0A324F818BE1D0CC6B0CF23C72CF1DBB7A57E2AA5CD4D2804ADF91419D86E1BFCCF61F24FA46CF297AE302841630C6AF05AE5882BC66C03767DF5F39876F703; flash=3_8Ycgg8CnaCXI_171pbii2DmAN-vhJMsESNXzxI74qnFzl3a_FB9oX9qYweUxe5UvZK1ZHWcSkdf5rmK8jPCWS2HRljXtqcZW6iJ_ZkJ2kh65_UrQqVNcd5iMiHufuXW49Mjq6ARZLXUALHnmIpd61biFrVt6-YdVmGfdX-ngluCvlzRn; light_key=AASBKE7rOxgWQziEhC_QY6ya8BVuLrKzALYsC_xDMi_xanlnQXvsZyYB4z1BWOfcoveGN7Qg; pin=DOOCN2017; unick=p85b1fnqr19fj0; VC_INTEGRATION_JSESSIONID=8a3c300d-1a41-497c-b163-d212d2b8ed6c; __jda=256578444.17325183358842067120209.1732518336.1733212947.1733279256.17; __jdc=256578444; __USE_NEW_PAGEFRAME__=false; __USE_NEW_PAGEFRAME_VERSION__=v9; _base_=YKH2KDFHMOZBLCUV7NSRBWQUJPBI7JIMU5R3EFJ5UDHJ5LCU7R2NILKK5UJ6GLA2RGYT464UKXAI5TPYU4VBBBWDQX6FGO2MU2LUEV4FSFUIHS4XEHPTQP4IKI3X7CJAJSPVORIFTBUVPCJUAGQKI352LNKFPOR42WQALLUAOV5DRD6AHODT4JN7KE5J2UD5T3SGLS6K5KW2RKKT6PEDIJOL37SFS6BM5IL564GRHB23AHIGVDWSQG6HLEQERDWYYBRKHS6ICOXUEJ2NZIJQ6SUQZYEDMZJDM3AAWL2W3Z6KPYGEG4MJ77GSNQL52J36DPJ7HQ6Y4NKZDKX3UU3CJVA765FVBSHIEWB5ZMRD422CLR3ZF5C2ZNGVWS2LERUANKDBXWKPJ4THBUUQGNCDLBKWTMXYIMNY7IB24FN6H3TRIPKULN5L36EJUXTT7GKMR6M65EU456IA6DQQPEJ4NVTYOGKM3ISJEC5XGOPBLKE677BPFI2A; b_belong=XWMCOEOLJD37J5GS2RT7LWCKUO7G67227B5DATCGB6JAT4QJVBRXU276EQYKZ3L67FGDS5XCG5JYNPURJMH7JNYIRJYOXL66W672HZL3EA467STZ6X3HQTON44WMGG46Q5U65IMIAR6VO3NPJP4CPPUJEJ4X6LTGMXSBVUA; __jdb=256578444.11.17325183358842067120209|17.1733279256',
            'origin': 'https://vcf.jd.com',
            'referer': 'https://vcf.jd.com/finance/saleBill/list/self',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        # 最多180天范围：{'data': {'code': '5', 'message': '时间范围不允许', 'success': False, 'total': 0}, 'success': True}
        # 没有页数和数据时：{"data": {"list": [], "message": "{}", "success": true, "total": 0}, "success": true}
        json_data = [
            {
                'bizType': '4',
                'pageSize': 500,
                'page': page,
                'refDateFrom': f'{self.startDate} 00:00:00',
                'refDateTo': f'{self.endDate} 23:59:59',
            },
        ]
        response = requests.post(
            'https://vcf.jd.com/api/finance/saleBill/list',
            headers=headers,
            cookies=self.cookies,
            json=json_data,
        )
        if response.status_code != 200:
            return {}
        return response.json()

    def fetch_all_data(self):
        """顺序获取所有页的数据"""
        page = 1
        datas = []
        while True:
            data_dict = self.fetch_page_data(page)
            """
            1、可以直接使用data = result['data'] 来获取值。区别： 'data' 键不存在，result['data'] 会抛出 KeyError 异常，而 get() 方法则会返回 None。
            2、.get()：在深层的字典中的某一级键不存在，那么 .get() 会返回 None，并且你不能在 None 上调用 .get()，否则会抛出 AttributeError。检查每一级的返回值是否为 None。
            3、extend()：将一个列表（或任何可迭代对象）的所有元素添加到另一个列表的末尾
            """
            value_dict = data_dict.get('data')
            if value_dict is None:
                return []
            elif value_dict.get('total') == 0:
                logger.info(f"京东自营京东自营--财务管理--结算管理--实销实结明细 {self.account} {self.startDate}~{self.endDate} 数据采集 {len(datas)} 完成")
                break
            else:
                page += 1
            datas += value_dict.get('list')
        return datas

    def process_data(self, total_page_data: list[dict]):
        """处理每条的数据"""
        for item in total_page_data:
            item["refDate"] = datetime.fromtimestamp(int(item["refDate"])/1000).strftime('%Y-%m-%d')
            item["dt"] = item["refDate"]
        return total_page_data

    def get_jd_fc_data(self, processed_data_all: list[dict]):
        self.tidb.insert_data(ods_cd_sl_jd_fc_solidsales_db_table, ods_cd_sl_jd_fc_solidsales_i_d_field_list,
                              processed_data_all)
        logger.info(f"京东自营京东自营--财务管理--结算管理--实销实结明细 {self.account} {self.startDate}~{self.endDate} 同步 {len(processed_data_all)} 完成")

    def main(self):
        jd_user_infos = self.tidb.get_user_info('JD')
        for jd_info in jd_user_infos:
            self.account = jd_info['account']
            self.cookies = self.get_cookies()
            if self.cookies is None:
                continue
            total_page_data = self.fetch_all_data()
            processed_data_all = self.process_data(total_page_data)
            self.get_jd_fc_data(processed_data_all)


if __name__ == "__main__":
    fetcher = fetcher_jd_fc_solidsales()
    fetcher.main()
