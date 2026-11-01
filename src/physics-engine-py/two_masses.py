# ! Quick Dirty AI generated file to test engine.py

import numpy as np
import pygame
from engine import System

W, H, SCALE = 800, 400, 150 # window size, pixels per metre
DT, FPS = 1e-3, 60 # physics step, frames per second

u = System()
a = u.add_mass(1, (-1, 0, 0), v=(-0.5, 0, 0)) # equal masses at rest length, moving apart
b = u.add_mass(1, (1, 0, 0), v=(0.5, 0, 0))
u.add_spring(a, b, k=5)

def to_screen(p): # side view: x right, y up, z ignored (always 0)
    return W / 2 + SCALE * p[0], H / 2 - SCALE * p[1]

def spring_points(p, q, coils=12, width=0.08):
    d = q[:2] - p[:2]
    n = np.array([-d[1], d[0]]) / np.linalg.norm(d) # perpendicular to the spring
    s = np.linspace(0, 1, 2 * coils + 1)
    zig = np.where(np.arange(len(s)) % 2, 1, -1) * width
    zig[0] = zig[-1] = 0
    return [to_screen(p[:2] + si * d + zi * n) for si, zi in zip(s, zig)]

pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
frame = 0
while not any(e.type == pygame.QUIT for e in pygame.event.get()):
    frame += 1
    u.run(DT, frame / FPS) # absolute target time, so rounding to whole steps doesn't accumulate
    screen.fill((20, 20, 30))
    pygame.draw.lines(screen, (200, 200, 200), False, spring_points(u.x[a], u.x[b]), 2)
    for i in (a, b):
        pygame.draw.circle(screen, (90, 170, 255), to_screen(u.x[i]), 18)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
