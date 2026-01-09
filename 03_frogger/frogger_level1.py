import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Frogger Level 1")

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()

frog_size = 40
frog = pygame.Rect(WIDTH//2 - frog_size//2, HEIGHT - frog_size, frog_size, frog_size)

car_width, car_height = 60, 40
cars = [pygame.Rect(random.randint(0, WIDTH - car_width), y, car_width, car_height) for y in range(200, 400, 60)]
car_speed = 5

log_width, log_height = 100, 40
logs = [pygame.Rect(random.randint(0, WIDTH - log_width), y, log_width, log_height) for y in range(60, 180, 60)]
log_speed = 3

font = pygame.font.SysFont(None, 48)

def draw_game():
    screen.fill(BLUE)
    pygame.draw.rect(screen, GREEN, (0, 400, WIDTH, 200))
    pygame.draw.rect(screen, BROWN, (0, 180, WIDTH, 60))

    for car in cars:
        pygame.draw.rect(screen, RED, car)
    for log in logs:
        pygame.draw.rect(screen, BROWN, log)
    pygame.draw.rect(screen, GREEN, frog)

def move_objects():
    for car in cars:
        car.x += car_speed
        if car.x > WIDTH:
            car.x = -car_width
    for log in logs:
        log.x -= log_speed
        if log.x < -log_width:
            log.x = WIDTH

def check_collision():
    for car in cars:
        if frog.colliderect(car):
            return True
    return False

def reset_game():
    frog.x = WIDTH//2 - frog_size//2
    frog.y = HEIGHT - frog_size
    for i, y in enumerate(range(200, 400, 60)):
        cars[i].x = random.randint(0, WIDTH - car_width)
    for i, y in enumerate(range(60, 180, 60)):
        logs[i].x = random.randint(0, WIDTH - log_width)

running = True
while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                frog.y -= frog_size
            elif event.key == pygame.K_DOWN:
                frog.y += frog_size
            elif event.key == pygame.K_LEFT:
                frog.x -= frog_size
            elif event.key == pygame.K_RIGHT:
                frog.x += frog_size
            elif event.key == pygame.K_r:
                reset_game()

    move_objects()
    if check_collision():
        text = font.render("You Died! Press R to Restart", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        continue

    draw_game()
    pygame.display.flip()

pygame.quit()
sys.exit()
