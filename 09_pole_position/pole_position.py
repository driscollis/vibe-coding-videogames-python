import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pole Position - Level 1")

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player car settings
player_img = pygame.Surface((40, 60))
player_img.fill(RED)
player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 100))
player_speed = 5
player_steer = 5

# Opponent car settings
opponent_img = pygame.Surface((40, 60))
opponent_img.fill(BLUE)
opponents = []
OPPONENT_SPEED = 3
SPAWN_INTERVAL = 60  # Frames between spawns

# Track settings
ROAD_WIDTH = 400
FINISH_LINE = 5000  # Distance in pixels to finish
scroll_y = 0
scroll_speed = 5

# Game variables
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 36)
game_state = "playing"
start_time = time.time()
best_time = float("inf")

# Main game loop
running = True
frame_count = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_state != "playing" and event.key == pygame.K_r:
            # Restart game
            game_state = "playing"
            scroll_y = 0
            player_rect.center = (WIDTH // 2, HEIGHT - 100)
            opponents.clear()
            start_time = time.time()

    if game_state == "playing":
        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > (WIDTH - ROAD_WIDTH) // 2:
            player_rect.x -= player_steer
        if keys[pygame.K_RIGHT] and player_rect.right < (WIDTH + ROAD_WIDTH) // 2:
            player_rect.x += player_steer
        if keys[pygame.K_UP]:
            scroll_y += scroll_speed
        if keys[pygame.K_DOWN]:
            scroll_y += scroll_speed * 0.5  # Slower backward movement

        # Spawn opponents
        frame_count += 1
        if frame_count % SPAWN_INTERVAL == 0:
            x = random.randint((WIDTH - ROAD_WIDTH) // 2 + 20, (WIDTH + ROAD_WIDTH) // 2 - 60)
            opponents.append(opponent_img.get_rect(topleft=(x, -60)))

        # Update opponents
        for opp in opponents[:]:
            opp.y += OPPONENT_SPEED
            if opp.top > HEIGHT:
                opponents.remove(opp)
            # Collision detection
            if player_rect.colliderect(opp):
                game_state = "game_over"
                break

        # Check win condition
        elapsed_time = time.time() - start_time
        if scroll_y >= FINISH_LINE:
            game_state = "win"
            if elapsed_time < best_time:
                best_time = elapsed_time

        # Check time limit (e.g., 90 seconds)
        if elapsed_time > 90:
            game_state = "game_over"

    # Drawing
    screen.fill(GREEN)  # Grass
    pygame.draw.rect(screen, GRAY, ((WIDTH - ROAD_WIDTH) // 2, 0, ROAD_WIDTH, HEIGHT))  # Road
    # White lines for road effect
    for y in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 10, (y - (scroll_y % 40)) % HEIGHT, 20, 10))

    # Draw player and opponents
    screen.blit(player_img, player_rect)
    for opp in opponents:
        screen.blit(opponent_img, opp)

    # Draw HUD
    timer_text = font.render(f"Time: {elapsed_time:.1f}s", True, WHITE)
    screen.blit(timer_text, (10, 10))
    distance_text = font.render(f"Distance: {scroll_y}/{FINISH_LINE}", True, WHITE)
    screen.blit(distance_text, (10, 50))
    if best_time != float("inf"):
        best_text = font.render(f"Best Time: {best_time:.1f}s", True, WHITE)
        screen.blit(best_text, (10, 90))

    # Game over or win screen
    if game_state == "game_over":
        text = font.render("Game Over! Press R to Restart", True, RED)
        screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
    elif game_state == "win":
        text = font.render(f"You Win! Time: {elapsed_time:.1f}s Press R to Restart", True, RED)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()