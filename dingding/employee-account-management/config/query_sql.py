# -*- coding: utf-8 -*-
# @Time     : 2024/12/20 10:28
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : query_sql.py


def query_sql_resignation_users(name: str = None) -> str:
    if name:
        return f"""
        select *
        from (select 'synology'                            as platform,
                     ddsulid.region,
                     ddsulid.uid,
                     ddsulid.name                          as username,
                     ddsulid.description                   as fullname,
                     ddsulid.email,
                     if(ddsulid.expired = 'now', '0', '1') as status
              from dim_prod.dim_dsd_synology_user_list_i_d ddsulid
              union all
              select 'lingxing'       as platform,
                     ''                  region,
                     ddlulid.uid,
                     ddlulid.username as username,
                     ddlulid.realname as fullname,
                     ddlulid.email,
                     ddlulid.status
              from dim_prod.dim_dsd_lx_user_list_i_d ddlulid
              union all
              select 'jushuitan'                            as platform,
                     ''                                        region,
                     ddjulid.userid                         as uid,
                     ddjulid.username                       as username,
                     ddjulid.username                       as fullname,
                     ddjulid.email,
                     if(ddjulid.enabled = 'true', '1', '0') as status
              from dim_prod.dim_dsd_jst_user_list_i_d ddjulid
              union all
              select 'ziniao'         as platform,
                     ''                  region,
                     ddzslid.userid   as uid,
                     ddzslid.username as username,
                     ddzslid.fullname as fullname,
                     ''               as email,
                     ddzslid.status   as status
              from dim_prod.dim_dsd_zn_staff_list_i_d ddzslid
              where ddzslid.userid != '17013976962864') as user
        where user.fullname = '{name}'
        """

    return """
    with common_table_dingding_employee as (select location as dingding_location,
                                                   name     as dingding_name
                                            from dim_prod.dim_dsd_yida_dd_employee_a_d
                                            where location != ''
                                            group by name)
    select 'synology'                                  as platform,
           synology_user.region,
           synology_user.uid,
           synology_user.name                          as username,
           synology_user.description                   as fullname,
           synology_user.email,
           if(synology_user.expired = 'now', '0', '1') as status,
           dingding_employee.dingding_name
    from dim_prod.dim_dsd_synology_user_list_i_d as synology_user
             left join common_table_dingding_employee as dingding_employee
                       on synology_user.description = dingding_employee.dingding_name
    where synology_user.name not in ('admin', 'guest', 'sync', 'nas', 'MeetingRoom', 'kingdee', 'dsd')
      and synology_user.expired != 'now'
      and dingding_employee.dingding_name is null
    union all
    # 查找已离职并且在领星没有停用的用户
    select 'lingxing'             as platform,
           ''                     as region,
           lingxing_user.uid,
           lingxing_user.username,
           lingxing_user.realname as fullname,
           lingxing_user.email,
           lingxing_user.status,
           dingding_employee.dingding_name
    from dim_prod.dim_dsd_lx_user_list_i_d as lingxing_user
             left join common_table_dingding_employee as dingding_employee
                       on lingxing_user.realname = dingding_employee.dingding_name
    where lingxing_user.uid not in
          ('200480', '211734', '10371441', '10131543', '10131544', '10131546', '10587441', '10588350')
      and lingxing_user.status = 1
      and dingding_employee.dingding_name is null
    union all
    # 查找已离职并且在聚水潭没有停用的用户
    select 'jushuitan'                                   as platform,
           ''                                            as region,
           jushuitan_user.userid                         as uid,
           jushuitan_user.username,
           jushuitan_user.username                       as fullname,
           jushuitan_user.email,
           if(jushuitan_user.enabled = 'true', '1', '0') as status,
           dingding_employee.dingding_name
    from dim_prod.dim_dsd_jst_user_list_i_d as jushuitan_user
             left join common_table_dingding_employee as dingding_employee
                       on jushuitan_user.username = dingding_employee.dingding_name
    where jushuitan_user.username not in
          ('DOOCN', '萨尼塔旗舰店', '劳保鞋品牌直销店', '跨境通用查询', '商品查询', 'F6库存查看', '开发部', '市场部',
           '贻庆食品',
           '共道旗舰店', '共道旗舰店:女神', 'jsp家居旗舰店:君', '分销库存查询', 'steelhead16家居旗舰店', '朗盟旗舰店',
           '德尔惠订单查看')
      and jushuitan_user.username not in ('Miya', '系统维护', '肖飞艳')
      and jushuitan_user.enabled = 'true'
      and dingding_employee.dingding_name is null
    union all
    # 查找已离职并且在紫鸟没有停用的用户
    select 'ziniao'            as platform,
           ''                  as region,
           ziniao_staff.userid as uid,
           ziniao_staff.username,
           ziniao_staff.fullname,
           ''                  as email,
           status              as status,
           dingding_employee.dingding_name
    from dim_prod.dim_dsd_zn_staff_list_i_d as ziniao_staff
             left join common_table_dingding_employee as dingding_employee
                       on ziniao_staff.fullname = dingding_employee.dingding_name
    where ziniao_staff.username not in ('fenlern', 'doocn01', 'doocn02', 'DoocnDSD')
      and ziniao_staff.fullname not in ('报名账号', '高雄顺', 'karen', '丘秀萍')
      and ziniao_staff.status = '1'
      and dingding_employee.dingding_name is null;
    """
