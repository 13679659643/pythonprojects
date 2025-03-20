# -*- coding: utf-8 -*-
from .global_state import global_state
from .log_config import CustomAccessFormatter
from .db_model import *

PROJECT_NAME = "employee-account-management"
# 补全项目名称(一定要写)
PROJECT_TITLE = "员工账号管理"
# 接口路由
PROJECT_ROUTE = f"/api/v1/{PROJECT_NAME}/schedule"

BASE_URL = "https://api.doocn.com:7000/api/v1/employee-account-management/schedule"

APP_TYPE = 'APP_VWP5WMVB2BLM0IP7IXDY'
SYSTEM_TOKEN = '7C766871KQABVU4770F6ZCMOZQE43XXSFGFIL92'


# https://api.doocn.com:7000/api/v1/employee-account-management/schedule/apply_for_role/get_lingxing_role_page
