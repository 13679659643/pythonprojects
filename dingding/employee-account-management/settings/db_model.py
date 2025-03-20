# -*- coding: utf-8 -*-
# @Time     : 2025/2/6 09:55
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : db_model.py

# 用户列表
# 表名
DB_TABLE_USER_LIST = 'dim_prod.dim_lx_user_list_i_h'
# 表字段
FIELD_LIST_USER_LIST = ['uid', 'status', 'user_name', 'real_name', 'mobile', 'email', 'is_master', 'sys_sub_admin_flag',
                        'login_num', 'create_time', 'last_login_ip', 'last_login_time']
# 创建表sql
CREATE_TABLE_USER_LIST = f"""
create table if not exists {DB_TABLE_USER_LIST}
(
    uid                bigint       not null comment '用户ID'
        primary key,
    status             int          not null comment '状态',
    user_name          varchar(100) not null comment '用户名',
    real_name          varchar(100) not null comment '真实姓名',
    mobile             varchar(20)  not null comment '手机号',
    email              varchar(100) not null comment '邮箱',
    is_master          tinyint(1)   not null comment '是否为主账号',
    sys_sub_admin_flag tinyint(1)   not null comment '系统子管理员标志',
    login_num          int          not null comment '登录次数',
    create_time        varchar(50)  not null comment '创建时间',
    last_login_ip      varchar(50)  not null comment '最后登录IP',
    last_login_time    varchar(50)  not null comment '最后登录时间'
)
    comment '领星-用户列表-刘云飞'
"""
# 清空表
TRUNCATE_TABLE_USER_LIST = f"""
truncate table {DB_TABLE_USER_LIST}
"""
# 重命名字段
RULES_USER_LIST = {
    # 'wxNickName': 'wx_nick_name',  # 微信昵称
    # 'orgNames': 'org_names',  # 组织名称
    # 'assPerDtos': 'ass_per_dtos',  # 关联人员DTOs
    # 'dingUsername': 'ding_user_name',  # 钉钉用户名
    # 'feishuUsername': 'feishu_user_name',  # 飞书用户名
    # 'isBindWX': 'is_bind_wx',  # 是否绑定微信
    # 'isBindJwt': 'is_bind_jwt',  # 是否绑定JWT
    # 'isBindBI': 'is_bind_bi',  # 是否绑定BI
    'uid': 'uid',  # 用户ID
    'realname': 'real_name',  # 真实姓名
    'mobile': 'mobile',  # 手机号
    'email': 'email',  # 邮箱
    'username': 'user_name',  # 用户名
    'zid': 'zid',  # 组织ID
    'is_master': 'is_master',  # 是否为主账号
    'status': 'status',  # 状态
    # 'seller': 'seller',  # 卖家
    # 'seller_ids': 'seller_ids',  # 卖家ID列表
    'login_num': 'login_num',  # 登录次数
    'create_time': 'create_time',  # 创建时间
    'last_login_ip': 'last_login_ip',  # 最后登录IP
    'last_login_time': 'last_login_time',  # 最后登录时间
    # 'role': 'role',  # 角色
    # 'editable': 'editable',  # 是否可编辑
    # 'warehouse': 'warehouse',  # 仓库
    'sysSubAdminFlag': 'sys_sub_admin_flag'  # 系统子管理员标志
}

# 用户信息
DB_TABLE_USER_INFO = 'dim_prod.dim_lx_user_info_i_h'
FIELD_LIST_USER_INFO = ['uid', 'status', 'status_desc', 'user_name', 'real_name', 'mobile', 'email', 'group_id', 'sid',
                        'email_relation_id', 'alibaba_id', 'warehouse_id', 'transparent_account_ids', 'user_org_dtos',
                        'org_sids', 'is_master', 'zid', 'company_id', 'nation_code', 'is_initial', 'name',
                        'new_store_status', 'org_names', 'is_org_master', 'ding_user_id', 'ding_user_name']
CREATE_TABLE_USER_INFO = f"""
create table if not exists {DB_TABLE_USER_INFO}
(
    uid                     bigint primary key not null comment '用户ID',
    status                  int                not null comment '状态',
    status_desc             varchar(100)       not null comment '状态描述',
    user_name               varchar(100)       not null comment '用户名',
    real_name               varchar(100)       not null comment '真实姓名',
    mobile                  varchar(20)        not null comment '手机号',
    email                   varchar(100)       not null comment '邮箱',
    group_id                json               not null comment '角色ID（JSON格式）',
    sid                     json               not null comment '店铺ID列表（JSON格式）',
    email_relation_id       json               not null comment '邮箱关联ID（JSON格式）',
    alibaba_id              json               not null comment '阿里巴巴ID（JSON格式）',
    warehouse_id            json               not null comment '仓库ID（JSON格式）',
    transparent_account_ids json               not null comment '透明账户ID（JSON格式）',
    user_org_dtos           json               not null comment '用户组织信息（JSON格式）',
    org_sids                json               not null comment '组织店铺ID列表（JSON格式）',
    is_master               boolean            not null comment '是否为主账号',
    zid                     bigint             not null comment 'ZID',
    company_id              bigint             not null comment '公司ID',
    nation_code             varchar(10)        not null comment '国家代码',
    is_initial              boolean            not null comment '是否为初始状态',
    name                    varchar(50)        not null comment '名称',
    new_store_status        boolean            not null comment '新店铺状态',
    org_names               varchar(50)        not null comment '组织名称',
    is_org_master           boolean            not null comment '是否为组织主账号',
    ding_user_id            varchar(100)       not null comment '钉钉用户ID',
    ding_user_name          varchar(100)       not null comment '钉钉用户名'
) comment '领星-用户详情列表-刘云飞';
"""
TRUNCATE_TABLE_USER_INFO = f"""
truncate table {DB_TABLE_USER_INFO}
"""
RULES_USER_INFO = {
    'uid': 'uid',  # 用户ID
    'mobile': 'mobile',  # 手机号
    'nationCode': 'nation_code',  # 国家代码
    'email': 'email',  # 邮箱
    'username': 'user_name',  # 用户名
    'zid': 'zid',  # 组织ID
    'companyId': 'company_id',  # 公司ID
    'isMaster': 'is_master',  # 是否为主账号
    'status': 'status',  # 状态
    'isInitial': 'is_initial',  # 是否为初始状态
    'statusDesc': 'status_desc',  # 状态描述
    'name': 'name',  # 名称
    'newStoreStatus': 'new_store_status',  # 新店铺状态
    'orgNames': 'org_names',  # 组织名称
    'isOrgMaster': 'is_org_master',  # 是否为组织主账号
    'dingUserId': 'ding_user_id',  # 钉钉用户ID
    'dingUsername': 'ding_user_name',  # 钉钉用户名
    'realname': 'real_name',  # 真实姓名
    'group_id': 'group_id',  # 组ID
    'sid': 'sid',  # SID
    'email_relation_id': 'email_relation_id',  # 邮箱关联ID
    'alibaba_id': 'alibaba_id',  # 阿里巴巴ID
    'warehouse_id': 'warehouse_id',  # 仓库ID
    'transparentAccountIds': 'transparent_account_ids',  # 透明账户ID列表
    'userOrgDtos': 'user_org_dtos',  # 用户组织DTOs
    'org_sids': 'org_sids',  # 组织SIDs
}

# 角色列表:
# 表名
DB_TABLE_ROLE_LIST = 'dim_prod.dim_lx_role_list_i_h'
# 表字段
FIELD_LIST_ROLE_LIST= [
    'id',
    'title',
    'description',
    'gmt_modified',
    'sys_sub_admin_flag',
    'status',
    'role_code',
    'role_group'
    ]
# 创建表sql
CREATE_TABLE_ROLE_LIST = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLE_ROLE_LIST}
(
    `id`                 varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
    `title`              varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '角色',
    `description`        varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '描述',
    `gmt_modified`       varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建时间',
    `sys_sub_admin_flag` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'sys_sub_admin_flag',
    `status`             varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'status',
    `role_code`          varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'role_code',
    `role_group`         varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'role_group',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='lx-设置-账号管理-角色管理-角色-辜涛';
"""
# 清空表
TRUNCATE_TABLE_ROLE_LIST = f"""
truncate table {DB_TABLE_ROLE_LIST}
"""
# 重命名字段
RULES_ROLE_LIST = {
    'id': 'id',  # 用户ID:10190547
    'title': 'title',  # 角色：子管理员
    'description': 'description',  # 描述：系统角色
    'gmt_modified': 'gmt_modified',  # 创建时间：2023-12-07 19:51:15
    'sysSubAdminFlag': 'sys_sub_admin_flag',  # 1
    'status': 'status',  # 1
    'roleCode': 'role_code',  # v9WkqR
    'roleGroup': 'role_group'  # ''
}



# 角色用户列表:
# 表名
DB_TABLE_ROLE_USER_LIST = 'dim_prod.dim_lx_role_user_list_i_h'
# 表字段
FIELD_LIST_ROLE_USER_LIST= [
    'id',
    'uid',
    'mobile',
    'email',
    'user_name',
    'zid',
    'company_id',
    'is_master',
    'status',
    'is_initial',
    'status_desc',
    'name',
    'is_org_Master',
    ]
# 创建表sql
CREATE_TABLE_ROLE_USER_LIST = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLE_ROLE_USER_LIST}
(
    `id`            varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
    `uid`           varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色用户ID',
    `mobile`        varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '手机号',
    `email`         varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '电子邮箱',
    `user_name`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '用户名',
    `zid`           varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'zid',
    `company_id`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '公司id',
    `is_master`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'is_master',
    `status`        varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'status',
    `is_initial`    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'is_initial',
    `status_desc`   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'status_desc',
    `name`          varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '姓名',
    `is_org_Master` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'is_org_Master',
    `real_name`     varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '真实姓名',
    PRIMARY KEY (`id`, `uid`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='lx-设置-账号管理-角色管理-角色用户-辜涛';
"""
# 清空表
TRUNCATE_TABLE_ROLE_USER_LIST = f"""
truncate table {DB_TABLE_ROLE_USER_LIST}
"""
# 重命名字段
RULES_ROLE_USER_LIST = {
    'id': 'id',  # 用户ID:10478557
    'uid': 'uid',  # 角色用户ID:10478557
    'mobile': 'mobile',  # 手机号
    'email': 'email',  # 电子邮箱
    'username': 'user_name',  # 用户名
    'zid': 'zid',  # :202480
    'companyId': 'company_id',  # 公司id
    'isMaster': 'is_master',  # :0
    'status': 'status',  # :1
    'isInitial': 'is_initial',  # :0
    'statusDesc': 'status_desc',  # :开启
    'name': 'name',  # 姓名
    'isOrgMaster': 'is_org_Master',  # :0
    'realname': 'real_name',  # 真实姓名
}



# 功能\字段列表:
# 表名
DB_TABLE_ACTION_PERM_LIST = 'dim_prod.dim_lx_role_action_perm_list_i_h'
# 表字段
FIELD_LIST_ACTION_PERM_LIST= [
    'id',
    'perm_id',
    'page_name',
    'module',
    'action',
    'action_child',
    'title',
    'name',
    'category',
    'sort',
    'action_sort',
    'is_select_perms',
    'select_perms_json',
    'cg_price',
    'ware_house_price_amount',
    'supplier',
    'lg_cost',
    ]
# 创建表sql
CREATE_TABLE_ACTION_PERM_LIST = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLE_ACTION_PERM_LIST}
(
    `id`                      varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
    `perm_id`                 varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户功能权限ID',
    `page_name`               varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '平台类(亚马逊/多平台)',
    `module`                  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '模块',
    `action`                  varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '功能',
    `action_child`            varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '二级功能',
    `title`                   varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '功能权限名称',
    `name`                    varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'name',
    `category`                varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'category',
    `sort`                    varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'sort',
    `action_sort`             varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'action_sort',
    `is_select_perms`         varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '功能权限是否勾选(1:已勾选,0:没有勾选)',
    `select_perms_json`       json                                   DEFAULT NULL COMMENT '已勾选的功能权限json格式',
    `cg_price`                varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '采购成本(1:可见,0:不可见,2:仅跟进人可见)',
    `ware_house_price_amount` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '库存单价、库存货值',
    `supplier`                varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '供应商',
    `lg_cost`                 varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物流费用',
    PRIMARY KEY (`id`, `perm_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='lx-设置-账号管理-角色管理-功能权限/字段权限-辜涛';
"""
# 清空表
TRUNCATE_TABLE_ACTION_PERM_LIST = f"""
truncate table {DB_TABLE_ACTION_PERM_LIST}
"""



# 数据权限列表:
# 表名
DB_TABLE_DATA_PERM_LIST = 'dim_prod.dim_lx_role_data_perm_list_i_h'
# 表字段
FIELD_LIST_DATA_PERM_LIST= [
    'type_name',
    'id',
    'module_name',
    'type_desc',
    'all_visible',
    'disabled',
    'type_value',
    'permission_org',
    'permission_owner',
    'type',
    ]
# 创建表sql
CREATE_TABLE_DATA_PERM_LIST = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLE_DATA_PERM_LIST}
(
    `type_name`        varchar(20) COLLATE utf8mb4_general_ci NOT NULL COMMENT '数据权限类型名称',
    `id`               varchar(20) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
    `module_name`      varchar(20) COLLATE utf8mb4_general_ci NOT NULL COMMENT '模块',
    `type_desc`        varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '功能',
    `all_visible`      varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '是否可见(1:可见,0:不可见)',
    `disabled`         varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'disabled',
    `type_value`       varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'type_value',
    `permission_org`   json                                   DEFAULT NULL COMMENT '用户',
    `permission_owner` json                                   DEFAULT NULL COMMENT '部门',
    `type`             varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '功能_us',
    PRIMARY KEY (`id`, `type_name`, `module_name`, `type_desc`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='lx-设置-账号管理-角色管理-数据权限(SKU、单据、全局日志、Listing、工具)-辜涛';
"""
# 清空表
TRUNCATE_TABLE_DATA_PERM_LIST = f"""
truncate table {DB_TABLE_DATA_PERM_LIST}
"""


# 手动-宜搭应用信息-辜涛
# 表名
DB_TABLE_YIDA_APPLICATION_INFO = 'dim_prod.dim_dsd_yida_application_i_m'


# 获取应用下的页面列表:
# 表名
DB_TABLE_YIDA_APPLICATION_CONTENTS = 'dim_prod.dim_dsd_yida_application_contents_i_m'
# 表字段
FIELD_LIST_YIDA_APPLICATION_CONTENTS= [
    'apply_name',
    'form_type',
    'creator',
    'form_uuid',
    'gmt_create',
    'title_zhCN',
    'title_enUS',
    'subject_domain',
    'third_level_directory',
    'form_name',
    'is_used',
    'is_delete',
    ]
# 创建表sql
CREATE_TABLE_YIDA_APPLICATION_CONTENTS = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLE_YIDA_APPLICATION_CONTENTS}
(
    `apply_name`            varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '应用名称',
    `form_type`             varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '表单应用类型',
    `creator`               varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建者',
    `form_uuid`             varchar(300) COLLATE utf8mb4_general_ci NOT NULL COMMENT '表单id',
    `gmt_create`            varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建时间',
    `title_zhCN`            varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '页面显示名称',
    `title_enUS`            varchar(70) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注:英文名称',
    `subject_domain`        varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '主题域',
    `third_level_directory` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '第三级文件目录',
    `form_name`             varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '表单名称',
    `is_used`               varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '是否使用',
    `is_delete`             varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '是否删除(1:未删除，0:已删除，初始化:2)',
    PRIMARY KEY (`form_uuid`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT ='yida-宜搭应用目录列表信息-辜涛';
"""
# 清空表
TRUNCATE_TABLE_YIDA_APPLICATION_CONTENTS = f"""
truncate table {DB_TABLE_YIDA_APPLICATION_CONTENTS}
"""
# 重命名字段
RULES_YIDA_APPLICATION_CONTENTS = {
    'apply_name': 'apply_name',  # 应用名称
    'formType': 'form_type',  # 表单应用类型
    'creator': 'creator',  # 创建者
    'formUuid': 'form_uuid',  # 表单id
    'gmtCreate': 'gmt_create',  # 创建时间
    'title_zhCN': 'title_zhCN',  # 页面显示名称
    'title_enUS': 'title_enUS',  # 备注:英文名称
    'subject_domain': 'subject_domain',  # 主题域
    'third_level_directory': 'third_level_directory',  # 第三级文件目录
    'form_name': 'form_name',  # 表单名称
    'is_used': 'is_used',  # 是否1使用
    'is_delete': 'is_delete',  # 是否删除(1:未删除，0:已删除，初始化:2)
}



# dwd_lx-设置-账号管理-角色管理-功能权限/角色用户-辜涛:
# 表名
DB_TABLE_ACTION_PERM_NOT = 'dwd_prod.dwd_lx_role_action_perm_list_i_h'

