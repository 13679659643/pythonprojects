# -*- coding: utf-8 -*-
# @Time    : 2025/2/19 16:32
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
from base import Base
from settings.db_model import *
# https://api.doocn.com:7000/api/v1/employee-account-management/schedule/apply_for_yida/get_yida_app_name


class TidbQueryDingdingData(Base):


    def get_yida_appinfo(self):
        """获取宜搭应用列表信息"""
        sql = f"""
        select app_type, apply_nick_name, system_token,user_id
        from {DB_TABLE_YIDA_APPLICATION_INFO}
        """
        query_resp = self.tidb_ob.query(sql)
        return query_resp.data

    def get_yida_app_name(self):
        """获取 宜搭应用列表 名称"""
        sql = f"""
        select apply_name as text,
               apply_name as value
        from {DB_TABLE_YIDA_APPLICATION_CONTENTS}
        where is_used = '1' and is_delete = 1
        group by apply_name
        order by apply_name
        """
        query_resp = self.tidb_ob.query(sql)
        return query_resp.data


    def get_content_subject_domain(self, apply_name):
        """通过应用名称 获取宜搭应用列表 主题域 名称"""
        sql = f"""
        select subject_domain as text,
               subject_domain as value
        from {DB_TABLE_YIDA_APPLICATION_CONTENTS}
        where apply_name = '{apply_name}' and is_used = '1' and is_delete = '1'
        group by subject_domain
        order by subject_domain
        """
        query_resp = self.tidb_ob.query(sql)
        return query_resp.data

    def get_content_third_level_directory(self, apply_name, subject_domain):
        """通过应用名称、主题域 获取宜搭应用列表 第三级文件目录 名称"""
        sql = f"""
        select third_level_directory as text,
               third_level_directory as value
        from {DB_TABLE_YIDA_APPLICATION_CONTENTS}
        where apply_name = '{apply_name}'
        and subject_domain = '{subject_domain}' and is_used = '1' and is_delete = '1' 
        group by third_level_directory
        order by third_level_directory
        """
        query_resp = self.tidb_ob.query(sql)
        return query_resp.data

    def get_content_form_name(self, apply_name, subject_domain, third_level_directory):
        """通过应用名称、主题域、第三级文件目录 获取宜搭应用列表 表单名称 名称"""
        sql = f"""
        select form_name as text,
               form_name as value
        from {DB_TABLE_YIDA_APPLICATION_CONTENTS}
        where apply_name = '{apply_name}'
        and subject_domain = '{subject_domain}'
        and third_level_directory = '{third_level_directory}'
        and is_used = '1' and is_delete = '1'
        group by form_name
        order by form_name
        """
        query_resp = self.tidb_ob.query(sql)
        return query_resp.data


if __name__ == '__main__':
    instance = TidbQueryDingdingData()
    print(instance.get_yida_appinfo())