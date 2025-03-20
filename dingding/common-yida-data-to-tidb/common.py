# _*_ coding: utf-8 _*_
# @Time : 2023/12/26
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : common-yida-data-to-tidb
# @Desc :
import json

from digiCore.db_init import InstantiationDB
from digiCore.read_yida_table import YidaTableTools
from jsonpath import jsonpath
from loguru import logger

from settings import dingding_access_token_name


class BaseSync:

    def __init__(self):
        self.idb = InstantiationDB()
        self.tidb_ob = self.idb.load_tidb_ob()
        self.redis_ob = self.idb.load_redis_ob()

    def get_config(self, from_uuid):
        """
        查询dim_dsd_yida_to_tidb_i_a表，获取字段映射字典
        """
        sql = f'select tidb_table_name, map_field_dict, app_type, system_token, user_id ' \
              f'from dim_prod.dim_dsd_yida_sync_i_manual where form_uuid="{from_uuid}" limit 1;'
        response = self.tidb_ob.query_one(sql)
        return response

    def get_dd_access_token(self):
        """
        获取钉钉的access_token
        """
        with self.redis_ob.conn as redis_conn:
            access_token = redis_conn.get(dingding_access_token_name)
            return access_token.decode().replace('"', '')

    def init_ding_core(self, config, form_uuid, access_token):
        """
        获取宜搭表单的数据
        """
        app_type = config.get('app_type')
        system_token = config.get('system_token')
        user_id = config.get('user_id')
        ding_core = YidaTableTools(app_type, system_token, form_uuid, user_id, access_token)
        ding_core.init_client()
        return ding_core

    def get_yida_field_map(self, ding_core):
        """
        获取宜搭表单的字段名称
        """
        item_define = ding_core.table_item_define()
        table_field_map_dict = {}
        table_field_id = jsonpath(item_define, '$[?(@.componentName=="FormContainer")]..fieldId')[0]

        child_field_map_dict = {}
        child_field = jsonpath(item_define, '$[?(@.componentName=="TableField")]..fieldId')

        for item in item_define:
            key = item.get('fieldId')
            lable = json.loads(item.get('label'))
            value = lable.get('zh_CN')
            # 获取子表的表头的映射字典
            if child_field and item.get('parentId') == child_field[0]:
                child_field_map_dict[key] = value
            # 获取表格字典映射字典
            elif item.get('parentId') == table_field_id:
                table_field_map_dict[key] = value
        return table_field_map_dict, child_field_map_dict

    def get_yida_table_data(self, ding_core, combined_dict):
        """
        获取宜搭表单数据
        """
        yida_table_data = []
        page_number = 1
        while True:
            data_list = ding_core.get_form_table_data(page_number)
            if not data_list:
                break
            for one in data_list:
                formData = one.get('formData')
                # 同时过滤formData并替换键
                updated_data = {combined_dict[k]: formData[k] for k in combined_dict if k in formData}
                yida_table_data.append(updated_data)
            page_number += 1
            logger.info(f'存在多页，正在采集第 {page_number} 页数据！')
        return yida_table_data

    def get_sub_table_data(self, ding_core, form_instance_id):
        """
        获取子表单的全部数据
        """
        page_number = 1
        data_list = []
        while True:
            result = ding_core.get_sub_from_table_data(form_instance_id, page_number=page_number)
            data = result.body.data
            if not data:
                break
            if len(data) < 50:
                data_list += data
                return data_list
            page_number += 1
            data_list += data
        return data_list

    def create_combined_dict(self, ding_core, config):
        """
        创建新的字段映射
        """
        table_field_map_dict, child_field_map_dict = self.get_yida_field_map(ding_core)
        if child_field_map_dict:
            field_map_dict = {**table_field_map_dict, **child_field_map_dict}
        else:
            field_map_dict = table_field_map_dict
        # 数据库中手动添加映射
        map_field_dict = json.loads(config.get('map_field_dict'))

        # 反转 map_field_dict，使其值映射到键
        reverse_map_field_dict = {v: k for k, v in map_field_dict.items()}

        # 创建新的组合字典
        combined_dict = {k: reverse_map_field_dict[v] for k, v in field_map_dict.items() if v in reverse_map_field_dict}

        return combined_dict

    def yida_data_to_tidb(self, config, combined_dict, yida_table_data):
        """
        将宜搭的表单数据保存到tidb数仓
        """
        db_table = config.get('tidb_table_name')
        field_list = [v for k, v in combined_dict.items()]
        data_list = yida_table_data
        self.tidb_ob.insert_data(db_table, field_list, data_list)

    def sync(self, form_uuid):
        """
        启动程序
        """
        config = self.get_config(form_uuid)
        access_token = self.get_dd_access_token()
        ding_core = self.init_ding_core(config, form_uuid, access_token)
        combined_dict = self.create_combined_dict(ding_core, config)
        yida_table_data = self.get_yida_table_data(ding_core, combined_dict)

        # 保存数据
        self.yida_data_to_tidb(config, combined_dict, yida_table_data)
