# -*- coding: utf-8 -*-
# @Time    : 2024/12/18 14:26
# @Author  : gu tao
# @Email   : 1370391119@qq.com
import base64
from io import BytesIO
import ddddocr
from PIL import Image
import requests
from digiCore.db.redis.core import RedisDao

from method import RetryDecorator


class CrawleromsLogisticData:
    def __init__(self):
        self.redis_client = RedisDao()


    @RetryDecorator.retry(max_attempts=3)
    def identify_verification_code(self):
        """
        验证码识别
        通过ddddocr 识别 t0c8 这种数字英文验证码
        :return:
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        response = requests.post('http://47.106.234.129:808/Login/GetCaptcha', headers=headers, verify=False)
        if response.status_code == 200:
            json_data = response.json()
            uuid = json_data.get('uuid')
            base64_img = json_data.get('img')
            # 将base64编码的图片数据解码为原始的二进制图片数据
            img_data = base64.b64decode(base64_img)
            # 使用 PIL.Image.open 方法从二进制数据中打开图片
            image = Image.open(BytesIO(img_data))
            image.save('oms_code.png')
            # 创建一个 ddddocr.DdddOcr 对象，用于进行OCR识别。
            ocr = ddddocr.DdddOcr(beta=True, show_ad=False)
            # 以二进制读模式打开 'ach_code.png'
            with open("oms_code.png", "rb") as image_file:
                # 　读取图片文件的内容
                image = image_file.read()
            # 　设置OCR识别的范围为数字和一些特定的运算符
            ocr.set_ranges("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
            # 对图片进行OCR识别，获取识别结果 ngkf
            img_expression = ocr.classification(image)
            if not img_expression:
                return None
            return uuid, img_expression
        return None

    @RetryDecorator.retry(max_attempts=3)
    def get_AccessToken(self):
        """
        获取登录标识 快驿通
        :return:
        """
        with self.redis_client.conn as redis_conn:
            if not redis_conn.exists(f"{self.HASH_AUTH_TOKEN}:{self.key}"):
                uuid_and_code = self.identify_verification_code()
                if uuid_and_code:
                    uuid, code = uuid_and_code
                    json_data = {
                        'username': self.config[self.logistics_provider_code]['username'],
                        'password': self.config[self.logistics_provider_code]['password'],
                        'code': code,
                        'uuid': uuid,
                    }
                    acc_response = self.session.post(self.token_url, json=json_data, verify=False)
                    if acc_response.status_code == 200:
                        access_token = acc_response.json()['accessToken']
                        redis_conn.hset(self.HASH_AUTH_TOKEN, self.key, access_token)
                        redis_conn.setex(f"{self.HASH_AUTH_TOKEN}:{self.key}", 2 * 60 * 60, "1")
                        logger.info("快驿通-登录账号成功")
                    else:
                        logger.warning(f"登录请求失败，状态码：{acc_response.status_code}")
                else:
                    logger.info("快驿通-获取验证码失败，重新获取验证码")

            return redis_conn.hget(self.HASH_AUTH_TOKEN, self.key)

    def main(self):
        uuid_and_code = self.identify_verification_code()
        print(uuid_and_code)
        exit()
        pass


if __name__ == "__main__":
    ahc = CrawleromsLogisticData()
    ahc.main()
