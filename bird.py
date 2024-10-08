import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 691
screen_height = 748

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Define game vars
ground_scroll = 0
scroll_speed = 4

# Load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')

run = True
while run:

    # fix the speed of the game
    clock.tick(fps)

    # Draw background
    screen.blit(bg, (0, 0))

    # Draw and scroll the ground
    screen.blit(ground_img, (ground_scroll, 614))
    ground_scroll -= scroll_speed
    if abs(ground_scroll) > 35:  # Passed the end of the ground
        ground_scroll = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
