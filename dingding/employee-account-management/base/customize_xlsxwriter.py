# -*- coding: utf-8 -*-
# @Time     : 2025/1/14 13:53
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : customize_xlsxwriter.py
# -*- coding: utf-8 -*-
# from typing import Union

import xlsxwriter.format
import xlsxwriter.worksheet


class MyWorkbook(xlsxwriter.Workbook):
    def __init__(self, filename=None, options=None):
        super(MyWorkbook, self).__init__(filename, options)

    # 初始化工作表样式
    def initialize_worksheet_style(
            self,
            worksheet: xlsxwriter.worksheet.Worksheet,
            set_column: dict = None,
            hide_gridlines_option: int = 1
    ) -> xlsxwriter.worksheet.Worksheet:
        """
        初始化工作表格式
        :param worksheet: 工作表
        :param set_column: 设置列宽
        :param hide_gridlines_option: 隐藏网格线
        :return:
        """
        for key, value in set_column.items():
            worksheet.set_column(key, value)

        worksheet.hide_gridlines(option=hide_gridlines_option)  # 隐藏网格线

        return worksheet

    # 获取单元格格式
    def get_worksheet_cell_format(
            self,
            font_name='Times New Roman',
            font_size=10,
            bold=False,
            align='center',
            valign='vcenter',
            text_wrap=True,
            border=1,
            **kwargs
    ) -> xlsxwriter.format.Format:
        """
        获取单元格格式
        :param font_name: 字体, 默认Times New Roman, 宋体
        :param font_size: 字体大小, 默认10
        :param bold: 字体, 默认不加粗
        :param align: 水平位置, 默认水平居中
        :param valign: 垂直位置, 默认垂直居中
        :param text_wrap: 默认, 自动换行
        :param border: 边框设置, 默认1
        :return:
        """
        properties = {
            'font_name': font_name,  # 字体
            'font_size': font_size,  # 字体大小
            'bold': bold,  # 加粗
            'align': align,  # 水平位置, 默认水平居中
            'valign': valign,  # 垂直位置, 默认垂直居中
            'text_wrap': text_wrap,  # 自动换行
            'border': border,  # 边框
        }
        properties.update(kwargs)  # 其他格式
        return self.add_format(properties)
