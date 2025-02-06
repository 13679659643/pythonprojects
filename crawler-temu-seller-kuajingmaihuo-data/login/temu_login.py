# -*- coding: utf-8 -*-
# @Time    : 2024/12/30 11:35
# @Author  : Night
# @File    : temu_login.py
# @Description:
import random

import execjs
import requests
from digiCore.message.to_webhook import ToWebhook
from loguru import logger
from base.crawler_base import RetryDecorator
from login.detect import onnx_model_main, find_target_gap
from login import get_file_path
from login.slide_track import GTrace
from base.crawler_base import CrawlerBase
from db._tidb import TidbConnector
from settings import dingding_api
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import base64


class AuthTemuLogin:
    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.public_key = ''
        self.verify_auth_token = ''
        self.session = requests.Session()
        self.gc = GTrace()
        self.dd_webhook = ToWebhook(dingding_api, atUserIds=['16765099110841587'])

    def decode_img(self, src):
        """
        针对图片进行解密
        :param src:
        :return:
        """
        with open(get_file_path('captcha_token.js'), 'r', encoding='utf-8') as fp:
            jsdata = fp.read()
        base64_img = execjs.compile(jsdata).call("decode_img", src)
        return base64_img

    def encrypt_d_captcha(self, distance, trace_list):
        """
        获取 captcha_collect
        :return:
        """
        with open(get_file_path('captcha_token.js'), 'r', encoding='utf-8') as fp:
            jsdata = fp.read()
        verify_code, captcha_collect = execjs.compile(jsdata).call("AuthToken", distance, trace_list,
                                                                   )
        return verify_code, captcha_collect

    @staticmethod
    def get_captcha_collect():
        """
        获取 captcha_collect
        :return:
        """
        with open(get_file_path('captcha_token.js'), 'r', encoding='utf-8') as fp:
            jsdata = fp.read()
        captcha_collect = execjs.compile(jsdata).call("getPrepareToken")
        return captcha_collect

    def get_password_publicKey(self):
        """
        获取登录密码 公钥
        :return:
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'cache-control': 'max-age=0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'origin': 'https://seller.kuajingmaihuo.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://seller.kuajingmaihuo.com/settle/seller-login?redirectUrl=https%3A%2F%2Fagentseller.temu.com%2Fmmsos%2Fmall-appeal.html&region=1&source=https%3A%2F%2Fagentseller.temu.com%2Fmain%2Fauthentication%3FredirectUrl%3Dhttps%253A%252F%252Fagentseller.temu.com%252Fmmsos%252Fmall-appeal.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i',
        }
        json_data = {}
        response = requests.post(
            'https://seller.kuajingmaihuo.com/bg/quiet/api/mms/key/login',
            headers=headers,
            json=json_data,
        )
        ret_data = response.json()
        public_key = ret_data['result']['publicKey']
        self.public_key = public_key

    def encrypt_rsa(self, encrypt_text):
        """
        RSA加密  传递公钥
        :param encrypt_text:
        :return:
        """
        public_key = f"""-----BEGIN PUBLIC KEY-----
                    {self.public_key}
        -----END PUBLIC KEY-----"""

        # 需要加密的数据
        data_to_encrypt = str(encrypt_text)

        # 导入公钥
        key = RSA.import_key(public_key)

        # 创建一个cipher对象
        cipher = PKCS1_v1_5.new(key)

        # 加密数据
        encrypted_data = cipher.encrypt(data_to_encrypt.encode())

        # 将加密后的数据转换为base64编码，以便于传输和存储
        encoded_encrypted_data = base64.b64encode(encrypted_data).decode()

        return encoded_encrypted_data

    def save_images(self, pictures):
        """
        保存图片  图片是Base64格式 需转换
        数组 0  背景图片
        数组 1  缺口图片
        "data:image/png;base64,iVBORw0KG
        :return:
        """
        bg_base64_str = self.decode_img(pictures[0]).split("base64,")[1]
        patch_base64_str = self.decode_img(pictures[1]).split("base64,")[1]
        with open('bg.png', 'wb') as png1:
            png1.write(base64.standard_b64decode(bg_base64_str))
        with open('patch.png', 'wb') as png1:
            png1.write(base64.standard_b64decode(patch_base64_str))

    def get_distance(self):
        """
        生成轨迹距离
        生成轨迹加密
        :return:
        """
        coordinate_onnx = onnx_model_main(get_file_path("bg.png"))
        distance = find_target_gap(coordinate_onnx, get_file_path("bg.png"), get_file_path("patch.png"))
        real_distance = round(distance * 272 / 320) - 5
        start_x = random.randint(28, 30)
        trace_list = self.gc.generate_track_list(real_distance, start_x)
        verify_code, captcha_collect = self.encrypt_d_captcha(real_distance, trace_list)
        return verify_code, captcha_collect

    def user_verify(self):
        """
        滑块轨迹验证
        :return:
        """
        verify_code, captcha_collect = self.get_distance()
        anti_content = CrawlerBase.get_anti_content()
        json_data = {
            'verify_code': verify_code,
            'captcha_collect': captcha_collect,
            'verify_auth_token': self.verify_auth_token,
            'anti_content': anti_content,
        }
        response = self.session.post('https://seller.kuajingmaihuo.com/api/phantom/user_verify',
                                     json=json_data)
        verify = response.json()['result']
        if verify == True:
            logger.info(f"验证码验证成功")
            return True
        # logger.info(response.json())

    @RetryDecorator.retry(max_attempts=10)
    def obtain_captcha(self):
        """
        获取验证码图片
        :return:
        """
        anti_content = CrawlerBase.get_anti_content()
        captcha_collect = self.get_captcha_collect()
        json_data = {
            'anti_content': anti_content,
            'verify_auth_token': self.verify_auth_token,
            'captcha_collect': captcha_collect,
        }
        response = self.session.post('https://seller.kuajingmaihuo.com/api/phantom/obtain_captcha',
                                     json=json_data)
        pictures = response.json()['pictures']

        if len(pictures) != 2:
            logger.info('---此图片是数字验证码---')
            return True
        # 保存图片
        self.save_images(pictures)
        # 滑块验证是否成功
        verification = self.user_verify()
        return verification

    def verify_login(self, encryptPassword='', attempt=0, max_attempts=3):
        """
        :return:
        """
        if attempt >= max_attempts:
            logger.error(f"Exceeded maximum attempts for . Aborting.")
            message = f'监控 <font color="red">TEMU : {self.account} </font> 登录失败'
            self.dd_webhook.send_markdown_message(message, '监控通知')
            return
        if not encryptPassword:
            encryptPassword = self.encrypt_rsa(self.password)
        json_data = {
            'loginName': self.account,
            'encryptPassword': encryptPassword,
            'keyVersion': '1',
        }
        # 指纹唯一
        cookies = {
            '_bee': 'q8qsSpWaHBzVmyHajf8JuxbrFf3saamk',
            'rckk': 'q8qsSpWaHBzVmyHajf8JuxbrFf3saamk',
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'cache-control': 'max-age=0',
            'anti-content': CrawlerBase().get_anti_content(),
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'origin': 'https://seller.kuajingmaihuo.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://seller.kuajingmaihuo.com/settle/seller-login?redirectUrl=https%3A%2F%2Fagentseller.temu.com%2Fmmsos%2Fmall-appeal.html&region=1&source=https%3A%2F%2Fagentseller.temu.com%2Fmain%2Fauthentication%3FredirectUrl%3Dhttps%253A%252F%252Fagentseller.temu.com%252Fmmsos%252Fmall-appeal.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i',
        }
        if self.verify_auth_token:
            headers['verifyauthtoken'] = self.verify_auth_token
            self.verify_auth_token = ''
        response = requests.post(
            'https://seller.kuajingmaihuo.com/bg/quiet/api/mms/login',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        ret_data = response.json()
        if ret_data['success'] is False and ret_data['errorMsg'] != '需要验证图形验证码':
            message = f'监控 <font color="red">Temu {self.account}</font> 接收手机验证码'
            self.dd_webhook.send_markdown_message(message, '监控通知')
            return {}
        verifyAuthToken = ret_data['result'].get('verifyAuthToken')
        if not verifyAuthToken:
            # 未出现验证码进行验证
            dict_cookie = dict(response.cookies)
            logger.info(f'Temu {self.account} 登录成功')
            return dict_cookie
        self.verify_auth_token = verifyAuthToken
        self.obtain_captcha()
        # 重新进行验证
        dict_cookie=self.verify_login(encryptPassword, attempt + 1, max_attempts)

        return dict_cookie

    def main(self):
        self.get_password_publicKey()
        return self.verify_login()


if __name__ == '__main__':
    tidb = TidbConnector()
    user_infos = tidb.get_user_info('TEMU')
    for temu_info in user_infos:
        temu_login = AuthTemuLogin(temu_info['account'], temu_info['password'])
        temu_login.main()
