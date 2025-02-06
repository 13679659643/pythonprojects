import random
from math import sin, cos, pi, log
from tkinter import *

# 将全局变量封装到一个字典中
config = {
    'CANVAS_WIDTH': 1900,
    'CANVAS_HEIGHT': 1000,
    'CANVAS_CENTER_X': 950,
    'CANVAS_CENTER_Y': 500,
    'IMAGE_ENLARGE': 11,
    'COLORS': ["#FF99CC", "#FFCC99", "#99CCFF", "#CC99FF", "#99FFCC", "#CCFF99"]
}


def center_window(root):
    width = config['CANVAS_WIDTH']
    height = config['CANVAS_HEIGHT']
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)


def heart_function(t, shrink_ratio: float = config['IMAGE_ENLARGE'], enlarge_factor: float = 1):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    x *= shrink_ratio * enlarge_factor
    y *= shrink_ratio * enlarge_factor
    x += config['CANVAS_CENTER_X']
    y += config['CANVAS_CENTER_Y']
    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())
    dx = ratio_x * (x - config['CANVAS_CENTER_X'])
    dy = ratio_y * (y - config['CANVAS_CENTER_Y'])
    return x - dx, y - dy


def shrink(x, y, ratio):
    force = -1 / (((x - config['CANVAS_CENTER_X']) ** 2 + (y - config['CANVAS_CENTER_Y']) ** 2) ** 0.6)
    dx = ratio * force * (x - config['CANVAS_CENTER_X'])
    dy = ratio * force * (y - config['CANVAS_CENTER_Y'])
    return x - dx, y - dy


def curve(p):
    return 2 * (2 * sin(4 * p)) / (2 * pi)


# 以下是对 Heart 类的优化
class Heart:
    def __init__(self, generate_frame=20):
        self.generate_frame = generate_frame
        self.all_points = {}
        for frame in range(generate_frame):
            self.calc(frame)

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)
        enlarge_factor = 1 + 0.05 * generate_frame
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))
        all_points = []
        heart_halo_point = self.create_points(halo_number, 11.6, enlarge_factor)
        for x, y in heart_halo_point:
            x += random.randint(-14, 14)
            y += random.randint(-14, 14)
            size = random.choice((1, 2, 2))
            all_points.append((x, y, size))
        _points = self.create_points(2000, config['IMAGE_ENLARGE'], enlarge_factor)
        for x, y in _points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))
        _edge_diffusion_points = self.create_points(3, config['IMAGE_ENLARGE'], enlarge_factor, 0.05, _points)
        for x, y in _edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
        _center_diffusion_points = self.create_points(4000, config['IMAGE_ENLARGE'], enlarge_factor, 0.17, _points)
        for x, y in _center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
        self.all_points[generate_frame] = all_points

    def create_points(self, number, shrink_ratio, enlarge_factor, beta=None, point_list=None):
        _points = set()
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio, enlarge_factor)
            if beta and point_list:
                x, y = scatter_inside(x, y, beta)
            _points.add((x, y))
        return _points

    @staticmethod
    def calc_position(x, y, ratio):
        force = 1 / (((x - config['CANVAS_CENTER_X']) ** 2 + (y - config['CANVAS_CENTER_Y']) ** 2) ** 0.520)
        dx = ratio * force * (x - config['CANVAS_CENTER_X']) + random.randint(-1, 1)
        dy = ratio * force * (y - config['CANVAS_CENTER_Y']) + random.randint(-1, 1)
        return x - dx, y - dy

    def render(self, render_canvas, render_frame):
        color = config['COLORS'][render_frame % len(config['COLORS'])]
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
        self.speed *= 0.98

    def render(self, render_canvas):
        render_canvas.create_rectangle(self.x, self.y, self.x + 2, self.y + 2, width=0, fill=self.color)

    def is_out_of_bounds(self):
        return self.x < 0 or self.y < 0 or self.x > config['CANVAS_WIDTH'] or self.y > config['CANVAS_HEIGHT']


class Explosion:
    def __init__(self, x, y, color, num_hearts=100):
        self.hearts = [SmallHeart(x, y, random.uniform(0, 2 * pi), random.uniform(1, 5), color) for _ in
                       range(num_hearts)]

    def move(self):
        for heart in self.hearts:
            heart.move()

    def render(self, render_canvas):
        for heart in self.hearts:
            heart.render(render_canvas)


def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, explosions: list, render_frame=0, explode_time=3000):
    render_canvas.delete('all')
    current_time = render_frame * 160
    if current_time < explode_time:
        render_heart.render(render_canvas, render_frame)
    else:
        handle_explosions(explosions, render_canvas)
    main.after(160, draw, main, render_canvas, render_heart, explosions, render_frame + 1)


def handle_explosions(explosions, render_canvas):
    if not explosions:
        create_explosions(explosions)
    for explosion in explosions:
        explosion.move()
        explosion.render(render_canvas)
    if all(heart.is_out_of_bounds() for explosion in explosions for heart in explosion.hearts):
        explosions.clear()
        create_explosions(explosions)


def create_explosions(explosions):
    for _ in range(400):
        x = random.randint(0, config['CANVAS_WIDTH'])
        y = random.randint(0, config['CANVAS_HEIGHT'])
        color = random.choice(config['COLORS'])
        explosions.append(Explosion(x, y, color, num_hearts=1))


if __name__ == '__main__':
    root = Tk()
    root.title("爱心")
    center_window(root)
    canvas = Canvas(root, bg='black', height=config['CANVAS_HEIGHT'], width=config['CANVAS_WIDTH'])
    canvas.pack()
    heart = Heart()
    explosions = []
    draw(root, canvas, heart, explosions)
    Label(root, text="I love you 欢", bg="black", fg="#FF99CC", font="Helvetic 20 bold").place(relx=.5, rely=.5,
                                                                                               anchor=CENTER)
    root.mainloop()
