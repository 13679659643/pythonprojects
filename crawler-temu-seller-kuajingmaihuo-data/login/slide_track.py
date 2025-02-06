# -*- coding: utf-8 -*-
# @Time    : 2024/10/31 17:20
# @Author  : Night
# @File    : vcp_login.py
# @Description:
import time

import random
import numpy as np
import ddddocr
from loguru import logger

from login.detect import onnx_model_main, find_target_gap


class SlideCrack(object):
    def __init__(self, gap, bg, out=None):
        """
        init code
        :param gap: 缺口图片
        :param bg: 背景图片
        :param out: 输出图片
        """
        self.gap = gap
        self.bg = bg
        self.out = out

    def discern(self):
        """
        图片缺口距离的识别
        :return:
        """
        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False, beta=True)

        with open(self.gap, 'rb') as f:
            target_bytes = f.read()

        with open(self.bg, 'rb') as f:
            background_bytes = f.read()

        res = det.slide_match(target_bytes, background_bytes)

        print(res)


class GTrace(object):

    def generate_bezier_curve(self, start_x, end_x, y, n_points=None):
        # 起始点和结束点
        P0 = np.array([start_x, y])
        P2 = np.array([end_x, y])

        # 控制点，这里简单设置为起始点和结束点的中间位置，但可以调整来改变曲线形状
        P1 = (P0 + P2) / 2

        # 如果没有指定点的数量，则根据距离动态计算
        if n_points is None:
            distance = end_x - start_x
            n_points = max(int(np.sqrt(distance) * 5), 10)  # 调整系数以适应不同的距离

        # 时间参数t从0到1均匀分布，但在接近终点时变化更慢
        t = np.linspace(0, 1, n_points)
        t = np.sqrt(t)  # 使用平方根函数使时间参数在接近终点时变化更慢

        # 计算贝塞尔曲线上的点
        bezier_points = np.array([(1 - t) ** 2 * P0 + 2 * (1 - t) * t * P1 + t ** 2 * P2 for t in t])

        return bezier_points

    def generate_track_list(self, distance, start_x=30, y=177.5, n_points=None):
        # 根据给定的距离计算结束位置
        end_x = start_x + distance

        # 生成贝塞尔曲线上的点
        bezier_points = self.generate_bezier_curve(start_x, end_x, y, n_points)

        # 构建轨迹列表
        track_list = []
        base_timestamp = int(time.time() * 1000)
        current_timestamp = base_timestamp
        # 初始化值
        track_list.append([start_x, y - 1, current_timestamp])
        for i, point in enumerate(bezier_points):
            x, _y = point
            random_offset = random.randint(20, 45)
            current_timestamp += random_offset  # 这里的时间间隔可以根据实际情况调整
            track_list.append([int(x), y, current_timestamp])

        return track_list

    def generate_custom_trajectory(self, start_x, base_timestamp, end_x=30, end_y=175, start_y=530, n_points_base=70,
                                   reduction=25,
                                   final_points=4):
        # 计算总距离
        total_distance = end_x - start_x
        total_distance_y = end_y - start_y
        # 动态计算轨迹列表的长度
        n_points = max(n_points_base - reduction, 20)  # 确保至少有20个点

        # 生成时间参数t从0到1均匀分布
        t = np.linspace(0, 1, n_points)

        # 使用指数衰减函数生成x坐标的变化
        x_coords = start_x + total_distance * (1 - np.exp(-5 * t))

        y_coords = start_y + total_distance_y * (1 - np.exp(-5 * t))

        # 确保最后一个点精确到达end_x
        if len(x_coords) > final_points:
            # 在最后final_points个点之间逐步精确到达end_x
            last_part = np.linspace(x_coords[-final_points - 1], end_x, final_points + 1)
            last_part_y = np.linspace(y_coords[-final_points - 1], end_y, final_points + 1)
            x_coords[-final_points:] = last_part[1:]
            y_coords[-final_points:] = last_part_y[1:]

        # 构建轨迹列表
        track_list = []
        timestamps = []
        base_timestamp -= random.randint(4500, 4684)  # 时间会相对提前
        current_timestamp = base_timestamp
        for i, (x, y) in enumerate(zip(x_coords, y_coords)):
            # 假设时间戳从某个起始值开始，每次增加相同的间隔
            random_offset = random.randint(20, 45)
            current_timestamp += random_offset  # 这里的时间间隔可以根据实际情况调整
            track_list.append([int(x), int(y), current_timestamp])
            timestamps.append(current_timestamp)

        # 结尾在加上
        end_timestamp = current_timestamp + random.randint(20, 30)
        track_list.append([end_x, int(end_y), end_timestamp])

        timestamps.append(end_timestamp)

        return track_list


if __name__ == '__main__':
    gc = GTrace()
    coordinate_onnx = onnx_model_main("bg.png")
    distance = find_target_gap(coordinate_onnx, "bg.png", "patch.png")
    logger.info(f'当前的距离是->{distance}')
    real_distance = round(distance * 272 / 320) - 5
    start_x = random.randint(28, 30)
    logger.info(f'当前的真实距离是->{real_distance}')
    aa = gc.generate_track_list(real_distance, start_x)
    logger.info(aa)
