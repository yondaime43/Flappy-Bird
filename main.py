import sys
import pygame
import os
import random

pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
pygame.init()


def draw_window():
    window.blit(bg_surface, (0, 0))
    pygame.display.update()


def draw_floor(floor):
    # first floor
    window.blit(floor_surface, (floor.x, floor.y))
    # second floor
    window.blit(floor_surface, (floor.x + WIDTH, floor.y))


def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(700, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(700, random_pipe_pos - 300))
    return bottom_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= HEIGHT:
            window.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            window.blit(flip_pipe, pipe)


def check_collision(pipes):
    global can_score

    for pipe in pipes:
        if bird.colliderect(pipe):
            can_score = True
            death_sound.play()
            return False

    if bird.top <= -100 or bird.bottom >= 800:
        can_score = True
        death_sound.play()
        return False

    return True


def check_pass():
    global score, can_score

    if pipe_list:
        for pipe in pipe_list:
            if 95 < pipe.centerx < 105 and can_score:
                score += 1
                score_sound.play()
                can_score = False
            if pipe.centerx < 0:
                can_score = True


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird


def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird.centery))
    return new_bird, new_bird_rect


def score_display(game_state):
    if game_state == 'main_game':
        score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 100))
        window.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 100))
        window.blit(score_surface, score_rect)

        high_score_surface = font.render(f"High Score: {high_score}", True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(WIDTH // 2, 750))
        window.blit(high_score_surface, high_score_rect)


def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score


# game variables
WIDTH, HEIGHT = 576, 924
fps = 120
gravity = 0.25
bird_movement = 0
score = 0
high_score = 0
can_score = True

# window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# font

font = pygame.font.Font('04B_19.TTF', 40)

# loading surfaces
bg_surface = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-day.png')),
                                    (WIDTH, HEIGHT)).convert()
floor_surface = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'base.png'))).convert()

pipe_surface = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'pipe-green.png'))).convert()

# bird surfaces
bird_downflap = pygame.transform.scale2x(
    pygame.image.load(os.path.join('assets', 'bluebird-downflap.png'))).convert_alpha()
bird_midflap = pygame.transform.scale2x(
    pygame.image.load(os.path.join('assets', 'bluebird-midflap.png'))).convert_alpha()
bird_upflap = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bluebird-upflap.png'))).convert_alpha()

bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird = bird_surface.get_rect(center=(100, HEIGHT // 2 - floor_surface.get_height() // 2))

birdflap = pygame.USEREVENT + 1
pygame.time.set_timer(birdflap, 200)

# pipe
pipe_list = []
pipe_height = [400, 600, 700]

# pipe event(spawning pipes)
spawnpipe = pygame.USEREVENT
pygame.time.set_timer(spawnpipe, 1200)

game_over_surface = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'message.png'))).convert_alpha()
game_over_rect = game_over_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

flap_sound = pygame.mixer.Sound(os.path.join('sound', 'sfx_wing.wav'))
death_sound = pygame.mixer.Sound(os.path.join('sound', 'sfx_die.wav'))
score_sound = pygame.mixer.Sound(os.path.join('sound', 'sfx_point.wav'))

game_on = True
clock = pygame.time.Clock()
floor = pygame.Rect(0, 800, floor_surface.get_width(), floor_surface.get_height())

while True:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_on:
                bird_movement = 0
                bird_movement -= 8
                flap_sound.play()
            if event.key == pygame.K_SPACE and game_on == False:
                game_on = True
                pipe_list.clear()
                bird.center = 100, HEIGHT // 2 - floor_surface.get_height() // 2
                bird_movement = 0
                score = 0

        if event.type == spawnpipe:
            pipe_list.extend(create_pipe())

        if event.type == birdflap:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            bird_surface, bird = bird_animation()

    window.blit(bg_surface, (0, 0))

    if game_on:
        # moving bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird.centery += bird_movement
        window.blit(rotated_bird, bird)
        game_on = check_collision(pipe_list)

        # Pipe
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score
        check_pass()
        score_display("main_game")
    else:
        window.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')

    # moving floor
    floor.x -= 1
    draw_floor(floor)
    if floor.x <= -576:
        floor.x = 0

    pygame.display.update()
