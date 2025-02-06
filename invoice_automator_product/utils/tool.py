# -*- coding: utf-8 -*-
# @Time    : 2024/9/18 16:22
# @Author  : Night
# @File    : tool.py
# @Description:
import hashlib
import requests


def md5_encrypt(text: str):
    md = hashlib.md5()
    md.update(text.encode('utf-8'))
    return md.hexdigest()


def upload_media(access_token: str, file_path: str):
    """
    文档路径 https://open.dingtalk.com/document/isvapp/upload-media-files
    :param access_token: 钉钉access_token
    :param file_path: 上传的文件路径
    :return: @xxx 返回唯一标识 media_id
    """
    params = {
        'access_token': access_token,
        'type': 'file'
    }
    with open(file_path, 'rb') as file:
        files = {
            'media': file,
        }
        response = requests.post('https://oapi.dingtalk.com/media/upload', params=params, files=files)
        result = response.json()
        if result['errmsg'] == 'ok':
            return result['media_id']
