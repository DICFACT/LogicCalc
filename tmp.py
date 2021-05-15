"""."""
from random import randint, choice

import pygame

screen = pygame.display.set_mode((400, 400))
screen.fill(0xFFFFFF)
done = False

DOTS = [
    (200, 0),
    (0, 400),
    (400, 400)
]

x, y = randint(0, 400), randint(0, 400)


for dot in DOTS:
    pygame.draw.circle(screen, 0xFF0000, dot, 2)


while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    dot = choice(DOTS)
    x, y = (dot[0] - x) / 2 + x, (dot[1] - y) / 2 + y
    screen.set_at((int(x), int(y)), 0x000000)

    pygame.display.update()

    if not pygame.key.get_pressed()[pygame.K_SPACE]:
        pygame.time.wait(200)
