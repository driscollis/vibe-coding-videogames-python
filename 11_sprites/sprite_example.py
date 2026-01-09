import pygame
import sys
import os

# -------------------------------------------------
# 1. INITIAL SETUP
# -------------------------------------------------
pygame.init()

# Window size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sprite Example")

# Clock for controlling FPS
clock = pygame.time.Clock()
FPS = 60

# -------------------------------------------------
# 2. LOAD THE SPRITE
# -------------------------------------------------
# Put your image (e.g. player.png) next to this script
SPRITE_PATH = "player64.png"

if not os.path.exists(SPRITE_PATH):
    print(f"ERROR: Sprite file '{SPRITE_PATH}' not found!")
    sys.exit(1)

# Load the image. The second argument makes the background transparent if the image has an alpha channel.
player_image = pygame.image.load(SPRITE_PATH).convert_alpha()

# Optional: scale the sprite
# player_image = pygame.transform.scale(player_image, (64, 64))

# -------------------------------------------------
# 3. CREATE A RECT (position & collision)
# -------------------------------------------------
# The Rect tracks where the sprite is on the screen.
player_rect = player_image.get_rect()
player_rect.center = (WIDTH // 2, HEIGHT // 2)   # start in the middle

# Movement speed (pixels per frame)
speed = 5

# -------------------------------------------------
# 4. MAIN GAME LOOP
# -------------------------------------------------
while True:
    # ----- Event handling -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ----- Input (arrow keys) -----
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_rect.x -= speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_rect.x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_rect.y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_rect.y += speed

    # Keep sprite inside the window
    player_rect.clamp_ip(screen.get_rect())

    # ----- Draw everything -----
    screen.fill((30, 30, 30))          # dark background
    screen.blit(player_image, player_rect)   # <--- draw the sprite
    pygame.display.flip()

    # ----- Cap the frame rate -----
    clock.tick(FPS)