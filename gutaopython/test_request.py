# -*- coding: utf-8 -*-
# @Time    : 2024/7/27 16:32
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    : 
# @Software:
import requests

headers = {
    'user-agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"

}

params = {"pagesize": 0, "pageno": 0, "reportno": "ORDERMX", "opentype": "find", "colen": "find", "userquery1": "0",
          "userquery2": "Z", "userquery4": "allqty", "userquery3": "%"}
# crtl+alt+l格式化
rsp = requests.post('http://8.134.39.115:8000/cms/tpl/list/values', json=params, headers=headers)
#print(type(rsp.text))  type 判断类型
#print(type(rsp.json()))



