# -*- coding: utf-8 -*-
# @Time    : 2024/9/27 14:03
# @Author  : Night
# @File    : delete_invoice_excel.py
# @Description: 删除excel文件
import os
import glob
from loguru import logger


class DelInvoiceExcel:
    def del_excel_file(self):
        """
        删除output下excel文件
        :return:
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        excel_files = glob.glob(os.path.join(script_dir, '../output', '*.xlsx'))
        for file_path in excel_files:
            try:
                os.remove(file_path)
                logger.info(f'已删除文件: {file_path}')
            except Exception as e:
                logger.info(f'删除文件 {file_path} 时出错: {e}')

    def main(self):
        self.del_excel_file()


if __name__ == '__main__':
    dle = DelInvoiceExcel()
    dle.main()
