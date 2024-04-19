import pygame as pg
import sys
import random as rd
from math import sqrt
from typing import Iterable

# use pyautogui to get the mouse position instead of pygame, so the mouse works outside of the window as well
from pyautogui import position
import ctypes
from ctypes import wintypes


class BG:
    def __init__(self, *colors: Iterable[Iterable[int]]) -> None:
        self.colors = colors
        self.r, self.g, self.b = colors[0][0], colors[0][1], colors[0][2]
        self.nextr, self.nextg, self.nextb = colors[1][0], colors[1][1], colors[1][2]
        self.ri, self.gi, self.bi = self.nextr-self.r, self.nextg-self.g, self.nextb-self.b
        self.enum = 0
        self.len_colors = len(colors)
        self.speed = 1
    
    def reset(self):
        enum2 = (self.enum+1) % self.len_colors
        self.r, self.g, self.b = self.colors[self.enum][0], self.colors[self.enum][1], self.colors[self.enum][2]
        self.nextr, self.nextg, self.nextb = self.colors[enum2][0], self.colors[enum2][1], self.colors[enum2][2]
        self.ri, self.gi, self.bi = self.nextr-self.r, self.nextg-self.g, self.nextb-self.b
        self.nextr = self.colors[enum2][0]
    
    # a function that makes the background change color slightly
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
            self.reset()


pg.init()

# getting the screen resolution
scrn_info = pg.display.Info()
WIDTH = scrn_info.current_w
HEIGHT = scrn_info.current_h

# WIDTH = 1600
# HEIGHT = 900

# ratios will help to change the size of objects depend on the screen resolution
width_ratio = WIDTH / 1920
height_ratio = HEIGHT / 1080
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Starfield by erfan :D")

FPS = 360

clock = pg.time.Clock()

# you can add a delay to your mouse
DELAY = 0

# storing the old mouse positions
mouse_pos = pg.mouse.get_pos()
old_xpos = mouse_pos[0]
old_ypos = mouse_pos[1]
timer = 0
old_positions: list[tuple[int, int]] = []



class Star(pg.Rect):
    def __init__(self, left: float, top: float, width: float, height: float, speedx: float, speedy: float):
        super().__init__(left, top, width, height)
        self.speedx = speedx
        self.speedy = speedy
        
        self.xpos: float = self.x
        self.ypos: float = self.y
        
        # saving the position that star has without counting the mouse interuption, so the star can get back to its original position
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


# the stars are able to spawn outside of screen
screen_edge_offset = 50

# stars speed will be a random number from -max_speed to max_speed
max_speed = 30

# a list to store all stars
stars: list[Star] = []

# number of stars (depends on the screen resolution)
n_stars = 185*width_ratio
# stars size (depends on the screen resolution)
star_radius = int(22*width_ratio)

def make_star(x: int=0, y: int=0):
    if not x:
        x = rd.randint(-screen_edge_offset, WIDTH+screen_edge_offset)
    if not y:
        y = rd.randint(-screen_edge_offset, HEIGHT+screen_edge_offset)
    
    speedx = (rd.randint(-max_speed, max_speed) + rd.random()*rd.choice((-1, 1))) * width_ratio
    speedy = (rd.randint(-max_speed, max_speed) + rd.random()*rd.choice((-1, 1))) * height_ratio
    star = Star(x, y, star_radius, star_radius, speedx, speedy)
    return star

# making 15 random sites for the stars to spawn so they don't ramdomly spawn in the screen
# instead they will ramdomly spawn in the sites so we have more like group of stars
n_sites = 15
n_stars_in_site = int(n_stars/n_sites)
# sites: list[tuple[int, int]] = []
site_min_width = int(100*width_ratio)
site_max_width = int(200*width_ratio)

# making the stars
for _ in range(n_sites):
    site_pos = (rd.randint(0, WIDTH), rd.randint(0, HEIGHT))
    site_width = rd.randint(site_min_width, site_max_width)
    for _2 in range(rd.randint(n_stars_in_site//2, int(n_stars_in_site*1.5))):
        star_dis_from_site_center_x = rd.randint(0, site_width)*rd.choice((-1, 1))
        star_dis_from_site_center_y = rd.randint(0, site_width)*rd.choice((-1, 1))
        star = make_star(site_pos[0]+star_dis_from_site_center_x, site_pos[1]+star_dis_from_site_center_y)
        stars.append(star)

# the invisible wall around your mouse :D (depends on the screen resolution)
mouse_line_radius = int(150 * width_ratio)

# the maximum distance the line connecting to stars can have (depends on the screen resolution)
stars_line_radius = int(110 * width_ratio)

# a function to make background gradient
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

# using polygons instead of lines because i can't figure out how to draw a transparent line :(
def draw_polygon_alpha(surface, color, points, width):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pg.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pg.Surface(target_rect.size, pg.SRCALPHA)
    pg.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points], width)
    surface.blit(shape_surf, target_rect)

# used to get the window position
def build_win_info_function():
    builder = ctypes.WINFUNCTYPE(
        wintypes.BOOL, wintypes.HWND, ctypes.POINTER(wintypes.RECT)
    )
    flags = ((1, "hwnd"), (2, "lprect"))
    func = builder(("GetWindowRect", ctypes.windll.user32), flags)
    return func

window_handler = pg.display.get_wm_info()["window"]
get_window_rect = build_win_info_function()

font = pg.font.SysFont("sans-serif", 40)

while True:
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                sys.exit()
        elif event.type == pg.QUIT:
            sys.exit()
    
    fps = clock.get_fps()
    dt = 1/fps if fps else 0.0
    
    # fill_surface(screen, colors)
    fill_surface(screen, ((50, 0, 25), (25, 0, 50)))
    # bg.fill(screen, dt)
    # screen.fill((25, 0, 50))
    
    # fps_text = font.render(f"fps: {fps:.5}", 0, "#ffffff")
    # screen.blit(fps_text, (10, 10))
    
    window_info = get_window_rect(window_handler)
    win_x = window_info.left + 8
    win_y = window_info.top + 31
    
    mouse_real_pos = position()
    old_positions.append((mouse_real_pos[0]-win_x, mouse_real_pos[1]-win_y))
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
        
        # mouse_pos = pg.mouse.get_pos()
        # mouse_pos_x = mouse_pos[0]
        # mouse_pos_y = mouse_pos[1]
        mouse_abs_pos = (old_xpos, old_ypos)
        x_distance = star.xpos+star.w//2 - mouse_abs_pos[0]
        y_distance = star.ypos+star.h//2 - mouse_abs_pos[1]
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
                line_width = int(stars_line_radius / actual_dis * 2.5)
                # pg.draw.line(screen, "#ffffff", star.center, other.center, line_width)
                color_multiplier = 255 - int(actual_dis / stars_line_radius * 255)
                draw_polygon_alpha(screen, (255, 255, 255, color_multiplier), (star.center, other.center, star.center), line_width)

        pg.draw.ellipse(screen, "#ffffff", star)
    
    if timer >= DELAY:
        old_xpos, old_ypos = old_positions[0]
        del old_positions[0]
        timer = DELAY
    
    timer += dt
    
    pg.display.flip()
    clock.tick(FPS)