import pygame
from pygame.locals import *
import random
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 691
screen_height = 748

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Splashy Fish')

# Define font
font = pygame.font.Font('font/PixelOperator-Bold.ttf', 60)

# Define color
white = (255, 255, 255)

# Define game vars
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_freq = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
pass_pipe = False

# Load images
bg = pygame.image.load('img/bg-water.png')
ground_img = pygame.image.load('img/ground-water.png')
button_img = pygame.image.load('img/restart.png')
top_scores_img = pygame.image.load('img/top_score.png')
top_scores_img = pygame.transform.scale(top_scores_img, (int(
    top_scores_img.get_width() * 0.1), int(top_scores_img.get_height() * 0.1)))

# File to store top scores
score_file = 'top_scores.txt'


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


def load_top_scores():
    if os.path.exists(score_file):
        with open(score_file, 'r') as f:
            scores = f.readlines()
        return [int(score.strip()) for score in scores]
    else:
        return [0, 0, 0]  # Default top 3 scores


def save_top_scores(new_score):
    top_scores = load_top_scores()
    top_scores.append(new_score)
    top_scores = sorted(top_scores, reverse=True)[:3]  # Keep only the top 3
    with open(score_file, 'w') as f:
        for score in top_scores:
            f.write(f"{score}\n")


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.vel = 0  # velocity
        self.clicked = False
        self.bounced = False

    def update(self):

        # Add gravity
        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8  # Speed cap
            if self.rect.bottom < 614:
                self.rect.y += int(self.vel)

        if game_over == False:
            # Add jumping
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Add rotation
            self.image = pygame.transform.rotate(
                self.images[self.index], self.vel * -2)
        else:
            if not self.bounced:
                self.vel = -10
                self.bounced = True

            self.vel += 0.5
            self.rect.y += int(self.vel)

            self.image = pygame.transform.rotate(self.images[self.index], 180)

            # if self.rect.top > screen_height:
            #    game_over = True


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()

        # Position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    # Make pipe move left
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:  # If pipe is off the screen
            self.kill()  # Remove the pipe from the group


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse is over the button
        # Whether or not the mouse collided with the rect of the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

# Create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)
# top_scores_but = Button(screen_width // 2 - 50, screen_height // 2 + 50, top_scores_img)
top_scores_but = Button(
    screen_width - top_scores_img.get_width() - 10, 10, top_scores_img)


top_scores = []
show_top_scores = False
score_saved = False
run = True
while run:

    # fix the speed of the game
    clock.tick(fps)

    # Draw background
    screen.blit(bg, (0, 0))

    # Draw bird group
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # Draw the ground
    screen.blit(ground_img, (ground_scroll, 614))

    # Check the score
    if len(pipe_group) > 0:  # When some pipes are on the screen
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # Look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    # Check if the bird has hit the ground
    if flappy.rect.bottom >= 614:
        game_over = True
        flying = False

    # This means game is running
    if game_over == False and flying == True:
        # Generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_freq:  # When enough time has passed
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(
                screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(
                screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # Draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:  # Passed the end of the ground
            ground_scroll = 0

        pipe_group.update()

    # Check for Game Over and reset
    if game_over == True:
        if not score_saved:
            save_top_scores(score)
            top_scores = load_top_scores()
            score_saved = True

        if button.draw() == True:
            game_over = False
            score = reset_game()
            score_saved = False
            show_top_scores = False

        if top_scores_but.draw():
            show_top_scores = True

        if show_top_scores:
            # Display the top scores
            draw_text("Top Scores:", font, white, screen_width //
                      2 - 100, screen_height // 2 + 100)
            for i, top_score in enumerate(top_scores):
                draw_text(f"{i + 1}: {top_score}", font, white, screen_width // 2 - 50,
                          screen_height // 2 + 150 + i * 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

pygame.quit()
