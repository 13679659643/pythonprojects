# -*- coding: utf-8 -*-
# @Time    : 2024/9/25 11:22
# @Author  : Night
# @File    : yida_download_attachments.py
# @Description:
from digiCore.common.decorate import def_retry
from digiCore.db.redis.core import RedisDao
import requests
from typing import Optional
from settings import USERID


class YidaDownloadAttachments:
    def __init__(self,
                 appType: str,
                 systemToken: str,
                 userId: Optional[str] = USERID
                 ):
        self.appType = appType
        self.systemToken = systemToken
        self.userId = userId
        self.redis = RedisDao()

    def init_headers(self):
        """
        初始化headers
        """
        access_token = self.redis.get_dingding_access_token()
        headers = {
            "x-acs-dingtalk-access-token": access_token
        }
        return headers

    @def_retry()
    def get_attachment_download_url(self, download_path):
        """
        获取附件的下载URL。

        参数:
        - download_path: str，附件的临时下载路径。

        返回:
        - str，附件的下载URL。
        """
        # 定义附件下载URL的API URL
        download_url = fr'https://api.dingtalk.com/v1.0/yida/apps/temporaryUrls/{self.appType}'
        # 构建请求体
        body = {
            'systemToken': self.systemToken,
            'userId': self.userId,
            'language': 'zh_CN',
            'fileUrl': download_path,
            'timeout': 3600
        }
        # 发送GET请求获取附件的下载URL
        response = requests.get(download_url, headers=self.init_headers(), params=body)
        # 返回附件的下载URL
        result = response.json() if response.status_code == 200 else {}
        return result.get('result')

    @def_retry()
    def get_attachment_io(self, url):
        """
        获取附件的IO流。

        :param url: 附件的下载URL。
        :return: 附件的IO流，如果下载失败则返回空字节串。
        """
        # 发送GET请求下载附件
        response = requests.get(url, headers=self.init_headers())
        # 返回附件的IO流
        return response.content if response.status_code == 200 else b''
