# -*- coding: utf-8 -*-
# @Time    : 2024/11/1 17:31
# @Author  : Night
# @File    : settings.py
# @Description:

# ---------------------------- project 配置 ----------------------------
PROJECT_NAME = "domestic-multi-channel-Login"
# 补全项目名称(一定要写)
PROJECT_TITLE = "国内多渠道自动化登录"
# 接口路由
prefix = f"/api/v1/{PROJECT_NAME}/schedule"

from enum import Enum


class RedisKeys(Enum):
    JD_LOGIN_KEY = PROJECT_NAME + ':jd:jd_vcp:login'
    JD_JM_LOGIN_KEY = PROJECT_NAME + ':jd:jd_jm:login'
    PDD_MMS_LOGIN_KEY = PROJECT_NAME + ':pdd:pdd_mms:login'
    # DW_STARK_LOGIN_KEY = PROJECT_NAME + ':dewu:dw_stark:login'
    # TB_MYSELLER_LOGIN_KEY = PROJECT_NAME + ':taobao:tb_seller:login'
    # VIS_VIP_LOGIN_KEY = PROJECT_NAME + ':vis:vis_vip:login'
    # TB_1688_LOGIN_KEY = PROJECT_NAME + ':taobao:tb_1688:login'
    # 可以继续添加其他键名