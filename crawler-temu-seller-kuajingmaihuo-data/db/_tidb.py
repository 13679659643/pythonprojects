# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:

import configparser
import os

from digiCore.db.tidb.core import TiDBDao


class TidbConnector(TiDBDao):
    def __init__(self):
        super().__init__()
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../', 'conf', 'config.ini')
        config.read(config_path, encoding='utf-8')
        tidb_host = config['tidb']['host']
        self.tidb_ob = TiDBDao(
            host=tidb_host
        )

    def get_user_info(self, platform):
        """
        获取用户信息
        :param platform: 站点
        :return:
        """
        sql = f"""
        SELECT * FROM dim_prod.dim_dsd_me_bus_employee_i_manual WHERE platform='{platform}'
        """
        result_list = self.tidb_ob.query_list(sql)
        return result_list


if __name__ == "__main__":
    tidb = TidbConnector()
