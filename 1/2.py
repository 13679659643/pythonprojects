import random
from math import sin, cos, pi, log
from tkinter import *

CANVAS_WIDTH = 1900
CANVAS_HEIGHT = 1000
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLARGE = 11
# 创建一个颜色列表
COLORS = ["#FF99CC", "#FFCC99", "#99CCFF", "#CC99FF", "#99FFCC", "#CCFF99"]


def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()  # 获取显示屏宽度
    screenheight = root.winfo_screenheight()  # 获取显示屏高度
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)  # 设置窗口居中参数
    root.geometry(size)  # 让窗口居中显示


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE, enlarge_factor: float = 1):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    # 放大
    x *= shrink_ratio * enlarge_factor
    y *= shrink_ratio * enlarge_factor
    # 移到画布中央
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    return 2 * (2 * sin(4 * p)) / (2 * pi)


class Heart:
    def __init__(self, generate_frame=20):
        self.generate_frame = generate_frame
        self.all_points = {}  # 每帧动态点坐标
        for frame in range(generate_frame):
            self.calc(frame)

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)
        enlarge_factor = 1 + 0.05 * generate_frame  # 增加一个放大因子
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))
        all_points = []
        # 光环
        heart_halo_point = set()
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio=11.6, enlarge_factor=enlarge_factor)
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1, 2, 2))
                all_points.append((x, y, size))
        # 轮廓
        _points = set()
        for _ in range(2000):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, enlarge_factor=enlarge_factor)
            _points.add((x, y))
        for x, y in _points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))
        # 内容
        _edge_diffusion_points = set()
        for _x, _y in list(_points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                _edge_diffusion_points.add((x, y))
        for x, y in _edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
        _center_diffusion_points = set()
        point_list = list(_points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            _center_diffusion_points.add((x, y))
        for x, y in _center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
        self.all_points[generate_frame] = all_points

    @staticmethod
    def calc_position(x, y, ratio):
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def render(self, render_canvas, render_frame):
        color = COLORS[render_frame % len(COLORS)]  # 选择颜色
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=color)


class SmallHeart:
    def __init__(self, x, y, direction, speed, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.color = color

    def move(self):
        self.x += self.speed * cos(self.direction)
        self.y += self.speed * sin(self.direction)
        self.speed *= 0.98  # 模拟空气阻力

    def render(self, render_canvas):
        render_canvas.create_rectangle(self.x, self.y, self.x + 2, self.y + 2, width=0, fill=self.color)

    def is_out_of_bounds(self):
        return self.x < 0 or self.y < 0 or self.x > CANVAS_WIDTH or self.y > CANVAS_HEIGHT


class Explosion:
    def __init__(self, x, y, color, num_hearts=100):
        self.hearts = [SmallHeart(x, y, random.uniform(0, 2 * pi), random.uniform(1, 5), color) for _ in range(num_hearts)]

    def move(self):
        for heart in self.hearts:
            heart.move()

    def render(self, render_canvas):
        for heart in self.hearts:
            heart.render(render_canvas)


def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, explosions: list, render_frame=0, explode_time=3000):
    render_canvas.delete('all')

    current_time = render_frame * 160  # 每帧的时间假设为160ms
    if current_time < explode_time:
        render_heart.render(render_canvas, render_frame)
    else:
        if not explosions:  # 如果尚未爆炸，则创建爆炸
            for _ in range(400):  # 创建20个小爱心爆炸
                x = random.randint(0, CANVAS_WIDTH)
                y = random.randint(0, CANVAS_HEIGHT)
                color = random.choice(COLORS)
                explosions.append(Explosion(x, y, color, num_hearts=1))  # 每个爆炸只包含一个小爱心
        for explosion in explosions:
            explosion.move()
            explosion.render(render_canvas)

        # 检查所有的小爱心，如果它们都移动到画布之外，就清空 explosions 列表并重新生成新的小爱心
        if all(heart.is_out_of_bounds() for explosion in explosions for heart in explosion.hearts):
            explosions.clear()
            for _ in range(400):  # 创建20个小爱心爆炸
                x = random.randint(0, CANVAS_WIDTH)
                y = random.randint(0, CANVAS_HEIGHT)
                color = random.choice(COLORS)
                explosions.append(Explosion(x, y, color, num_hearts=1))  # 每个爆炸只包含一个小爱心

    main.after(160, draw, main, render_canvas, render_heart, explosions, render_frame + 1)




if __name__ == '__main__':
    root = Tk()
    root.title("爱心")
    center_window(root, CANVAS_WIDTH, CANVAS_HEIGHT)  # 窗口居中显示
    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()
    explosions = []
    draw(root, canvas, heart, explosions)
    Label(root, text="I love you 欢", bg="black", fg="#FF99CC", font="Helvetic 20 bold").place(relx=.5, rely=.5,
                                                                                               anchor=CENTER)
    root.mainloop()

