import pygame
import sys
import os

# -------------------------------------------------
# 1. INITIAL SETUP
# -------------------------------------------------
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animated Sprite Example")

clock = pygame.time.Clock()
FPS = 60

# -------------------------------------------------
# 2. LOAD SPRITE SHEET & EXTRACT FRAMES
# -------------------------------------------------
SPRITE_SHEET_PATH = "walk_sheet.png"  # Your sprite sheet (e.g., 128x128, 4 frames 32x32)

if not os.path.exists(SPRITE_SHEET_PATH):
    print(f"ERROR: Sprite sheet '{SPRITE_SHEET_PATH}' not found! Download one.")
    sys.exit(1)

# Load the full sheet
sheet = pygame.image.load(SPRITE_SHEET_PATH).convert_alpha()

# Sprite settings (adjust to your sheet!)
FRAME_WIDTH, FRAME_HEIGHT = 32, 32   # Size of each frame
FRAMES_PER_ROW = 4                   # Horizontal frames in sheet
ANIM_SPEED = 0.2                     # Frames per game frame (lower = slower)

# Extract frames into a list
frames = []
for i in range(FRAMES_PER_ROW):
    rect = pygame.Rect(i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
    frame = sheet.subsurface(rect)
    frames.append(frame)

# Idle frame (first one)
idle_frame = frames[0]

# -------------------------------------------------
# 3. SPRITE SETUP
# -------------------------------------------------
player_rect = frames[0].get_rect()
player_rect.center = (WIDTH // 2, HEIGHT // 2)

speed = 5
frame_idx = 0          # Current animation frame
anim_timer = 0         # For frame timing

# -------------------------------------------------
# 4. MAIN LOOP
# -------------------------------------------------
while True:
    # ----- Events -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ----- Input & Movement -----
    keys = pygame.key.get_pressed()
    moving = False
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_rect.x -= speed
        moving = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_rect.x += speed
        moving = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_rect.y -= speed
        moving = True
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_rect.y += speed
        moving = True

    # Keep in bounds
    player_rect.clamp_ip(screen.get_rect())

    # ----- Animate -----
    if moving:
        anim_timer += 1
        if anim_timer > 1 / ANIM_SPEED:  # Advance frame
            frame_idx = (frame_idx + 1) % len(frames)
            anim_timer = 0
        current_image = frames[frame_idx]
    else:
        current_image = idle_frame

    player_rect.size = current_image.get_size()  # Update rect for new image

    # ----- Draw -----
    screen.fill((30, 30, 30))
    screen.blit(current_image, player_rect)
    pygame.display.flip()

    clock.tick(FPS)