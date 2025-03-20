# -*- coding: utf-8 -*-
# @Time     : 2025/1/24 15:34
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : tidb_query_lingxing_data.py
# Tidb查询领星数据
from base import Base
from settings.db_model import *


class TidbQueryLingxingData(Base):

    def get_store_platform_data(self):
        """宜搭展示亚马逊平台"""
        sql = """
        select 'Amazon' as text,
        # '10001'  as value
        'Amazon'  as value
        union all
        select platform_name as text,
               platform_name as value
        from (select platform_name
                     # ,platform_name
              from dim_prod.dim_gsm_lx_mp_store_i_d
              group by platform_name
              order by platform_name) origin;
        """
        tidb_resp = self.tidb_ob.query(sql)
        return tidb_resp.data

    def get_amazon_store_data(self):
        """宜搭展示亚马逊店铺lxamseller"""
        sql = """
        select SUBSTRING_INDEX(store, '-', LENGTH(store) - LENGTH(REPLACE(store, '-', ''))) as text,
               SUBSTRING_INDEX(store, '-', LENGTH(store) - LENGTH(REPLACE(store, '-', '')))  as value
        from dim_prod.dim_gsm_lx_mp_store_i_d
        where platform_name = 'Amazon'
        order by store;
        """
        tidb_resp = self.tidb_ob.query(sql)
        return tidb_resp.data

    def get_mutil_platform_store_data(self, platform_code):
        """宜搭展示多平台店铺lxmpseller"""
        sql = f"""
        select store as text,
               store  as value
        from dim_prod.dim_gsm_lx_mp_store_i_d
        where platform_name = '{platform_code}'
        order by store;
        """
        tidb_resp = self.tidb_ob.query(sql)
        return tidb_resp.data

    def get_amazon_store_site(self, platform_code, store):
        """宜搭展示亚马逊店铺站点"""
        sql = f"""
        select SUBSTRING_INDEX(store, '-', -1) as text,
               SUBSTRING_INDEX(store, '-', -1)  as value
        from dim_prod.dim_gsm_lx_mp_store_i_d
        where platform_name = '{platform_code}'
        and SUBSTRING_INDEX(store, '-', LENGTH(store) - LENGTH(REPLACE(store, '-', ''))) = '{store}'
        order by store;
        """
        tidb_resp = self.tidb_ob.query(sql)
        return tidb_resp.data

    def get_user_info_data(self, real_name):
        """
        账号信息
        """
        sql = f"""
        select ddydead.name,
               ddydead.mobile,
               ddydead.email,
               ifnull(dluilih.user_name, concat('DOOCN-', substring_index(ddydead.email, '@', 1))) as user_name,
               if(dluilih.user_name is null, 'Doocn0258', '******')                             as user_password,
               ifnull(dluilih.real_name, ddydead.name)                                             as real_name,
               ifnull(dluilih.status_desc, '等待创建')                                             as status_desc,
               dluilih.sid
        from dim_prod.dim_dsd_yida_dd_employee_a_d ddydead
                 left join {DB_TABLE_USER_INFO} dluilih
                           on dluilih.real_name = ddydead.name
        where ddydead.name = '{real_name}'
        limit 1;
        """
        tidb_resp = self.tidb_ob.query(sql, fetch='one')
        return tidb_resp.data

    def get_user_list(self):
        sql = f"""
        select *
        from {DB_TABLE_USER_LIST}
        """
        query_resp = self.tidb_ob.query(sql)

        return query_resp.data

    def get_role_page_data(self):
        sql = f"""
        select page_name as text,
               page_name as value
        from {DB_TABLE_ACTION_PERM_NOT}
        group by page_name
        order by page_name;
        """
        tidb_resp = self.tidb_ob.query(sql)
        return tidb_resp.data

    def get_role_module_data(self, page_name, real_name):
        sql = f"""
        # 获取模块名称
        select module as text,
               module as value
        from {DB_TABLE_ACTION_PERM_NOT}
        where page_name = '{page_name}'
        and name = '{real_name}'
        group by module
        order by module;
        """
        tidb_resp = self.tidb_ob.query(sql)
        return tidb_resp.data

    def get_role_action_data(self, page_name, module_name, real_name):
        sql = f"""
        # 获取功能名称
        select concat(action, if(action_child = '', '', concat('_', action_child))) as text,
               concat(action, if(action_child = '', '', concat('_', action_child))) as value
        from {DB_TABLE_ACTION_PERM_NOT}
        where page_name = '{page_name}'
          and module = '{module_name}'
          and name = '{real_name}'
        group by concat(action, action_child)
        order by concat(action, action_child);
        """
        tidb_resp = self.tidb_ob.query(sql)
        return tidb_resp.data

    def get_role_perm_data(self, page_name, module_name, action_name, real_name):
        action_list = action_name.split('_')
        if len(action_list) == 1:
            action = action_list[0]
            action_child = ''
        else:
            action = action_list[0]
            action_child = action_list[1]
        sql = f"""
        # 获取权限名称
        select title as text,
               title as value
        from {DB_TABLE_ACTION_PERM_NOT}
        where page_name = '{page_name}'
          and module = '{module_name}'
          and action = '{action}'
          and action_child = '{action_child}'
          and name = '{real_name}'
        group by title
        order by title
        """
        tidb_resp = self.tidb_ob.query(sql)
        return tidb_resp.data


if __name__ == '__main__':
    instance = TidbQueryLingxingData()
    # print(instance.get_lingxing_role_page())
    # print(instance.get_lingxing_role_module('亚马逊'))
    # print(instance.get_lingxing_role_action('亚马逊', '订单'))
    # print(instance.get_lingxing_role_perm('亚马逊', '客服', '评价管理_review'))
    # print(instance.get_amazon_store_data())
    print(instance.get_role_page_data())
