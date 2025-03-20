# -*- coding: utf-8 -*-
# @Time    : 2025/2/19 15:25
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:

import json
import logging
import time
from typing import List, Any

from base import Base
from common import Utils
from crawler import LingxingCrawler
from crawler.dingding import DingdingCrawler
from schema import general_response_decorator, GeneralResponseSchema
from script.dingding import TidbQueryDingdingData
from settings.db_model import *
from script.lingxing.tidb_query_lingxing_data import TidbQueryLingxingData


class TidbInsertDingdingData(Base):
    def __init__(self):
        super().__init__()
        self.dingding_crawler = DingdingCrawler()
        self.tidb_query_lingxing = TidbQueryDingdingData()

    @staticmethod
    def split_title(title_enUS):
        if '/' in title_enUS:
            parts = title_enUS.split('/')
            if len(parts) >= 3:
                return {
                    'subject_domain': parts[0],
                    'third_level_directory': parts[1],
                    'form_name': parts[2],
                    'is_used': 1
                }
            else:
                # 如果分割后的部分不足3个，可以根据需要处理
                return {
                    'subject_domain': title_enUS,
                    'third_level_directory': title_enUS,
                    'form_name': title_enUS,
                    'is_used': 0
                }
        else:
            return {
                'subject_domain': title_enUS,
                'third_level_directory': title_enUS,
                'form_name': title_enUS,
                'is_used': 0
            }

    def update_is_delete_status(self, yida_formuuid: list):
        """更新已删除的表单信息"""
        # 获取数据量form_uuid
        select_sql = f"""
        select form_uuid from {DB_TABLE_YIDA_APPLICATION_CONTENTS} 
        """

        # set 去重
        db_form_uuid = self.tidb_ob.query(select_sql).data
        yida_formuuid_set = set(yida_formuuid)

        diff_ab = [f"""'{item['form_uuid']}'""" for item in db_form_uuid if item['form_uuid'] not in yida_formuuid_set]
        if not diff_ab:
            return
        # 拼接 → '%s,%s,%s'
        placeholders = ','.join(diff_ab)

        # 构建参数化查询
        update_sql = f"""
            UPDATE {DB_TABLE_YIDA_APPLICATION_CONTENTS} 
            SET is_delete = IF(
                  form_uuid IN ({placeholders}),  -- 添加引号
                  '0',  -- 匹配时设为已删除
                  '1'   -- 不匹配时设为未删除
                )
        """
        self.tidb_ob.commit_sql(update_sql)



    # 插入数据权限
    @general_response_decorator(description='插入领星角色数据权限', is_message=1)
    def insert_yida_application_contents(self):
        yida_appinfo = self.tidb_query_lingxing.get_yida_appinfo()
        self.tidb_ob.commit(CREATE_TABLE_YIDA_APPLICATION_CONTENTS)
        # self.tidb_ob.commit(TRUNCATE_TABLE_DATA_PERM_LIST)
        insert_list = []
        check_formuuid = []
        for appinfo in yida_appinfo:
            try:

                resp = self.dingding_crawler.get_contents_shujujishi(appinfo['app_type'], appinfo['system_token']
                                                                     , appinfo['user_id'])
                apply_name = appinfo['apply_nick_name']

                data_list = resp.data
                for item in data_list:
                    split_title = self.split_title(item.get("title_enUS", "None"))
                    check_formuuid.append(item.get('formUuid', "None"))
                    new_form = item.copy()
                    new_form['apply_name'] = apply_name
                    new_form['subject_domain']= split_title.get("subject_domain", "None")
                    new_form['third_level_directory'] = split_title.get('third_level_directory', "None")
                    new_form['form_name'] = split_title.get("form_name", "None")
                    new_form['is_used'] = split_title.get("is_used", "None")
                    new_form['is_delete'] = '1'
                    insert_list.append(new_form)
            except TypeError:
                logging.info(f"Error occurred with id: {appinfo}")
                continue
        # 重命名字段
        rename_rules = [Utils.replace_dict_key({**item}, RULES_YIDA_APPLICATION_CONTENTS) for item in insert_list]

        insert_resp = self.tidb_ob.insert(DB_TABLE_YIDA_APPLICATION_CONTENTS, FIELD_LIST_YIDA_APPLICATION_CONTENTS, rename_rules)
        logging.basicConfig(level=logging.INFO)
        logging.info(str(insert_resp))
        self.update_is_delete_status(check_formuuid)
        logging.info('更新表单状态成功！')
        return insert_resp.message


if __name__ == '__main__':
    instance = TidbInsertDingdingData()
    print(instance.insert_yida_application_contents())
