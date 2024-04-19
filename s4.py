import pygame as pg
import sys
import random as rd
from math import sqrt
from typing import Iterable


pg.init()

scrn_info = pg.display.Info()
WIDTH = scrn_info.current_w
HEIGHT = scrn_info.current_h

# WIDTH = 1600
# HEIGHT = 900

width_ratio = WIDTH / 1920
height_ratio = HEIGHT / 1080
screen = pg.display.set_mode((WIDTH, HEIGHT))

FPS = 360

clock = pg.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class BG:
    def __init__(self, *colors: Iterable[Iterable[int]]) -> None:
        self.colors = colors
        self.r, self.g, self.b = colors[0][0], colors[0][1], colors[0][2]
        self.nextr, self.nextg, self.nextb = colors[1][0], colors[1][1], colors[1][2]
        self.ri, self.gi, self.bi = self.nextr-self.r, self.nextg-self.g, self.nextb-self.b
        self.enum = 0
        self.len_colors = len(colors)
        self.speed = 1
    
    def init(self):
        enum2 = (self.enum+1) % self.len_colors
        self.r, self.g, self.b = self.colors[self.enum][0], self.colors[self.enum][1], self.colors[self.enum][2]
        self.nextr, self.nextg, self.nextb = self.colors[enum2][0], self.colors[enum2][1], self.colors[enum2][2]
        self.ri, self.gi, self.bi = self.nextr-self.r, self.nextg-self.g, self.nextb-self.b
        self.nextr = self.colors[enum2][0]
    
    def fill(self, surface: pg.Surface, dt: float):
        surface.fill((self.r, self.g, self.b))
        
        self.r += self.ri*dt*self.speed
        self.g += self.gi*dt*self.speed
        self.b += self.bi*dt*self.speed
        
        if self.r > 255:
            self.r = 255
        elif self.r < 0:
            self.r = 0
        
        if self.g > 255:
            self.g = 255
        elif self.g < 0:
            self.g = 0
        
        if self.b > 255:
            self.b = 255
        elif self.b < 0:
            self.b = 0
        
        if int(self.r) == self.nextr and int(self.g) == self.nextg and int(self.b) == self.nextb:
            self.enum = (self.enum+1) % self.len_colors
            self.init()


class Star(pg.Rect):
    def __init__(self, left: float, top: float, width: float, height: float, speedx: float, speedy: float):
        super().__init__(left, top, width, height)
        self.speedx = speedx
        self.speedy = speedy
        self.xpos: float = self.x
        self.ypos: float = self.y
        self.original_xpos = self.x
        self.original_ypos = self.y
    
    
    def move(self, dt: float):
        self.original_xpos += self.speedx * dt
        self.original_ypos += self.speedy * dt
        
        xdis = self.original_xpos - self.xpos
        ydis = self.original_ypos - self.ypos
        self.xpos += xdis * dt
        self.ypos += ydis * dt
        
        self.x = self.xpos
        self.y = self.ypos


max_speed = 40
stars: list[Star] = []
n_dots = int(169*width_ratio)
dot_radius = int(24*width_ratio)
screen_edge_offset = 60

def make_star(x: int=0, y: int=0):
    if not x:
        x = rd.randint(-screen_edge_offset, WIDTH+screen_edge_offset)
    if not y:
        y = rd.randint(-screen_edge_offset, HEIGHT+screen_edge_offset)
    
    speedx = (rd.randint(-max_speed, max_speed) + rd.random()*rd.choice((-1, 1))) * width_ratio
    speedy = (rd.randint(-max_speed, max_speed) + rd.random()*rd.choice((-1, 1))) * height_ratio
    star = Star(x, y, dot_radius, dot_radius, speedx, speedy)
    return star


for _ in range(n_dots):
    star = make_star()
    stars.append(star)

mouse_line_radius = int(169 * width_ratio)
stars_line_radius = int(120 * width_ratio)

def fill_surface(surface: pg.Surface, colors: Iterable):
    l_colors_1 = len(colors) - 1
    
    h = surface.get_height()
    w = surface.get_width()
    for i in range(l_colors_1):
        r, g, b = colors[i][0], colors[i][1], colors[i][2]
        
        r_interval = (colors[i+1][0] - r) / h * l_colors_1
        g_interval = (colors[i+1][1] - g) / h * l_colors_1
        b_interval = (colors[i+1][2] - b) / h * l_colors_1
        
        for j in range(h//l_colors_1 * i, h//l_colors_1 * (i+1)):
            pg.draw.line(surface, (r, g, b), (0, j), (w, j))
            r += r_interval
            g += g_interval
            b += b_interval
            
            if r > 255:
                r = 255
            elif r < 0:
                r = 0
            
            if g > 255:
                g = 255
            elif g < 0:
                g = 0
            
            if b > 255:
                b = 255
            elif b < 0:
                b = 0

colors = ((100, 0, 0), (100, 0, 100), (0, 0, 100), (0, 100, 100), (0, 100, 0), (100, 100, 0), (100, 0, 0))
bg = BG(*colors)

def draw_polygon_alpha(surface, color, points, width):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pg.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pg.Surface(target_rect.size, pg.SRCALPHA)
    pg.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points], width)
    surface.blit(shape_surf, target_rect)

while True:
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                sys.exit()
        elif event.type == pg.QUIT:
            sys.exit()
    
    fps = clock.get_fps()
    dt = 0.0
    if fps != 0:
        dt = 1/fps
    
    pg.display.set_caption(f"fps: {fps}")
    # fill_surface(screen, colors)
    fill_surface(screen, ((70, 10, 35), (35, 10, 70)))
    # bg.fill(screen, dt)
    # screen.fill((25, 0, 50, 0))
    for i, star in enumerate(stars):
        star.move(dt)
        if star.left > WIDTH+screen_edge_offset or star.right < -screen_edge_offset or star.top > HEIGHT+screen_edge_offset or star.bottom < -screen_edge_offset:
            del stars[i]
            new_star = rd.choice((make_star(rd.choice((rd.randint(-screen_edge_offset, 0), rd.randint(WIDTH, WIDTH+screen_edge_offset))),
                                            rd.randint(-screen_edge_offset, HEIGHT+screen_edge_offset)),
                                  make_star(rd.randint(-screen_edge_offset, WIDTH+screen_edge_offset),
                                            rd.choice((rd.randint(-screen_edge_offset, 0), rd.randint(HEIGHT, HEIGHT+screen_edge_offset))))))
            stars.append(new_star)
            break
        
        mouse_pos = pg.mouse.get_pos()
        x_distance = star.centerx - mouse_pos[0]
        y_distance = star.centery - mouse_pos[1]
        actual_distance = sqrt(x_distance*x_distance + y_distance*y_distance)
        
        if actual_distance and actual_distance < mouse_line_radius:
            ratio = mouse_line_radius / actual_distance
            new_x_dis = x_distance * ratio
            new_y_dis = y_distance * ratio
            star.xpos += new_x_dis - x_distance
            star.ypos += new_y_dis - y_distance
        
        for other in stars[i + 1 :]:
            x_dis = star.centerx - other.centerx
            y_dis = star.centery - other.centery
            actual_dis = sqrt(x_dis*x_dis + y_dis*y_dis)
            
            if actual_dis and actual_dis < stars_line_radius:
                line_width = int(stars_line_radius / actual_dis * 3)
                # pg.draw.line(screen, "#ffffff", star.center, other.center, line_width)
                color_multiplier = 255 - int(actual_dis / stars_line_radius * 255)
                draw_polygon_alpha(screen, (255, 255, 255, color_multiplier), (star.center, other.center, star.center), line_width)
        
        pg.draw.ellipse(screen, "#ffffff", star)
    
    
    pg.display.flip()
    clock.tick(FPS)