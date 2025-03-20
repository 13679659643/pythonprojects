# -*- coding: utf-8 -*-
# @Time    : 2025/2/14 10:26
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:

import json
import requests
from typing import Dict, List, Any
from base import Base
from common import Utils
from schema import GeneralResponseSchema, general_response_decorator
from requests import Session

from settings import RULES_YIDA_APPLICATION_CONTENTS


class DingdingCrawler(Base):
    # URL_CONTENTS_SHUJUJISHI_INFO = 'https://tgyn0g.aliwork.com/dingtalk/web/APP_VWP5WMVB2BLM0IP7IXDY/query/formnav/getFormNavigationListByOrder.json'

    @general_response_decorator(description='获取数据集市目录列表', is_message=0)
    def get_contents_shujujishi(self, appType: str, systemToken: str, userId: str) -> list[Any]:
        """
        获取数据集市等宜搭应用目录列表
        # report:报表、
        # view:表单-->实际显示的页面
        # manage:流程表单页面上显示的页面
        # receipt:表单开发预览页面
        # process:流程表单开发预览页面
        # display:自定义界面、
        # portal:门户、
        # datav:大屏
        :return:
        """
        contents = []
        formTypes = ['view', 'process', 'report', 'display', 'portal', 'datav', 'manage', 'receipt']
        for formType in formTypes:
            url = 'https://api.dingtalk.com/v1.0/yida/forms'
            # view,process,report,display,portal,datav,manage
            params = {
                'appType': appType,
                'systemToken': systemToken,
                'userId': userId,  # 杨哥
                'language': 'zh_CN',
                'formTypes': formType,
            }

            response = self.dingding_api_session.get(url=url, params=params)
            contents_list = self.check_requests_response(response)['result']['data']
            processed_contents_list = self.contents_shujujishi_analysis(contents_list)
            contents.extend(processed_contents_list)

        return contents

    @staticmethod
    def contents_shujujishi_analysis(contents: dict):
        processed_list = []
        for content in contents:
            new_form = content.copy()  # 复制原始字典，避免修改原数据
            # 检查是否存在 'title' 键
            if 'title' in new_form:
                title = new_form.pop('title')  # 移除 'title' 键并获取其值
                # 提取 zhCN 和 enUS 的值，如果不存在则设为 None
                new_form['title_zhCN'] = title.get('zhCN', None)
                new_form['title_enUS'] = title.get('enUS', None)
            processed_list.append(new_form)
        return processed_list

    # @property
    # def access_token(self) -> Dict:
    #     """
    #     获取钉钉access_token
    #     :return:
    #     """
    #     with self.redis_ob.conn as conn:
    #         access_token = conn.get('common-dingding-access-token:common:access_token').decode()
    #         return {'access_token': access_token.replace('"', '')} if access_token else {}
    #
    # @staticmethod
    # def return_result(response_request):
    #     """
    #     返回数据错误检查
    #     :param response_request:
    #     :return:
    #     """
    #     assert response_request.status_code == 200, '接口请求失败'
    #     result_status = response_request.json()
    #     assert result_status.get('errcode') == 0, result_status.get('errmsg')
    #     return result_status.get('result')
    #
    # @general_response_decorator(description='获取钉钉企业部门列表')
    # def get_department_list(self, parent_id='') -> GeneralResponseSchema:
    #     """
    #     获取企业所有部门列表
    #     parent_id: 父部门id
    #     :return:
    #     """
    #     url = 'https://oapi.dingtalk.com/topapi/v2/department/listsub'
    #     data = {
    #         'dept_id': parent_id
    #     }
    #     dept_list = []
    #
    #     response = requests.post(url, params=self.access_token, data=json.dumps(data))
    #     result = self.return_result(response)
    #
    #     for dept_info in result:
    #         dept_id = dept_info.get('dept_id')
    #         parent_id = dept_info.get('parent_id')
    #         name = dept_info.get('name')
    #         dic = {'dept_id': dept_id, 'parent_id': parent_id, 'name': name}
    #         dept_list.append(dic)
    #         dept_list += self.get_department_list(dept_id)['data']
    #     return dept_list
    #
    # @general_response_decorator(description='获取指定部门中的用户基本信息')
    # def get_department_employee_list(self, dept_id):
    #     """
    #     获取指定部门中的用户基本信息
    #     :return:
    #     """
    #     url = 'https://oapi.dingtalk.com/topapi/user/listsimple'
    #     # url = 'https://oapi.dingtalk.com/topapi/v2/user/list'
    #     data = {
    #         "dept_id": dept_id,
    #         'cursor': 0,
    #         'size': 10
    #     }
    #     staff_list = []
    #     while True:
    #         response = requests.post(url, params=self.access_token, data=json.dumps(data))
    #         result = self.return_result(response)
    #         for staff in result.get('list'):
    #             staff.update({'dept_id': dept_id})
    #             staff_list.append(staff)
    #         if result.get('has_more'):
    #             data['cursor'] = result.get('next_cursor')
    #         else:
    #             break
    #     return staff_list
    #
    # @general_response_decorator(description='获取指定员工的详细信息')
    # def get_employee_information(self, userid='1623977055815157'):
    #     """
    #     获取用户详细信息
    #     :param userid: 用户id
    #     :return:
    #     """
    #     url = 'https://oapi.dingtalk.com/topapi/v2/user/get'
    #     data = {
    #         'userid': userid
    #     }
    #
    #     response = requests.post(url, params=self.access_token, data=json.dumps(data))
    #     result = self.return_result(response)
    #     return result
    #
    # @general_response_decorator(description='获取员工花名册')
    # def get_roster(self):
    #     """
    #     获取员工花名册
    #     :return:
    #     """
    #     url = 'https://oapi.dingtalk.com/topapi/smartwork/hrm/employee/queryonjob'
    #     data = {
    #         'status_list': '2,3,5,-1',
    #         'offset': 0,
    #         'size': 50
    #     }
    #     response = requests.post(url, params=self.access_token, data=json.dumps(data))
    #     result = self.return_result(response)
    #     return result
    #
    # @general_response_decorator(description='获取员工花名册详细信息')
    # def get_roster_information(self, userid: str = '1623977055815157'):
    #     """
    #     获取员工花名册详细信息
    #     :return:
    #     """
    #     url = 'https://oapi.dingtalk.com/topapi/smartwork/hrm/employee/v2/list'
    #     data = {
    #         'userid_list': userid,
    #         'agentid': 1
    #     }
    #     response = requests.post(url, params=self.access_token, data=json.dumps(data))
    #     result = self.return_result(response)
    #
    #     staff_info = dict()
    #     for field_data in result[0].get('field_data_list'):
    #         field_name = field_data.get('field_name')
    #         field_value_list = field_data.get('field_value_list')
    #
    #         # print(field_data)
    #         # 获取第一个
    #         first_value = field_value_list[0].get('label', '')
    #         # 获取全部值
    #         all_value = ','.join([dept.get('label', '') for dept in field_value_list])
    #
    #         if field_name == '姓名':
    #             staff_info['name'] = first_value
    #         elif field_name == '手机号':
    #             staff_info['mobile'] = first_value.replace('+86-', '')
    #         elif field_name == '邮箱':
    #             staff_info['email'] = first_value
    #         elif field_name == '办公地点':
    #             staff_info['location'] = first_value
    #         elif field_name == '职位':
    #             staff_info['position'] = first_value
    #         elif field_name == '部门id':
    #             staff_info['dept_id'] = all_value
    #         elif field_name == '部门':
    #             staff_info['dept_name'] = all_value
    #         elif field_name == '主部门id':
    #             staff_info['main_dept_id'] = all_value
    #         elif field_name == '主部门':
    #             staff_info['main_dept_name'] = all_value
    #         elif field_name == '直属主管':
    #             staff_info['report_to'] = first_value
    #         # elif field_name == '学历':
    #         #     staff_info['education'] = first_value
    #         # elif field_name == '毕业院校':
    #         #     staff_info['graduation_institution'] = first_value
    #         # elif field_name == '住址':
    #         #     staff_info['address'] = first_value
    #         # elif field_name == '年龄（系统计算）':
    #         #     staff_info['age'] = first_value
    #
    #     return staff_info


if __name__ == '__main__':
    obj = DingdingCrawler()
    print(obj.get_contents_shujujishi('APP_VWP5WMVB2BLM0IP7IXDY', '7C766871KQABVU4770F6ZCMOZQE43XXSFGFIL92',
                                      '16566389302394979'))
    # for item in obj.get_contents_shujujishi('APP_VWP5WMVB2BLM0IP7IXDY','7C766871KQABVU4770F6ZCMOZQE43XXSFGFIL92','16566389302394979').data:
    #
    #     print(item)
