import pygame
import random
import sys
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

PLAYER_SPEED = 5
BULLET_SPEED = 7
INVADER_SPEED = 1
INVADER_DROP_SPEED = 20

# ──────────────────────────────────────────────────────────────
# Load and prepare sprites (add this near the top)
# ──────────────────────────────────────────────────────────────
def load_image(name, scale=None):
    path = os.path.join("assets", name)
    image = pygame.image.load(path).convert_alpha()
    if scale:
        image = pygame.transform.scale(image, scale)
    return image

# Player sprite (you can make it animated too later if you want)
PLAYER_IMG = load_image("player.png", (60, 50))   # adjust size as needed

# Invader animation frames
INVADER_FRAMES = [
    load_image("invader1.png", (40, 30)),
    load_image("invader2.png", (40, 30))
]

# Optional: explosion animation frames (if you want later)
# EXPLOSION_FRAMES = [load_image(f"explosion{i}.png") for i in range(1,7)]

class Player:
    def __init__(self, x, y):
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = PLAYER_SPEED

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Invader:
    def __init__(self, x, y):
        self.frames = INVADER_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = INVADER_SPEED
        self.direction = 1

        # Animation timing
        self.animation_timer = 0
        self.animation_delay = 400  # milliseconds between frames (adjust for speed)

    def update(self):
        self.rect.x += self.speed * self.direction

        # Simple animation: switch frame every X ms
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.animation_timer = current_time

    def drop_down(self):
        self.rect.y += INVADER_DROP_SPEED
        self.direction *= -1

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Game objects
        # CHANGED CODE
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)  # adjusted Y
        # CHANGED CODE
        self.bullets = []
        self.invaders = []
        self.invader_bullets = []

        # Game state
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.level = 1

        # Create invaders
        self.create_invaders()

        # Timing
        self.last_shot = 0
        self.invader_shoot_timer = 0

    def create_invaders(self):
        self.invaders = []
        rows = 5
        cols = 11
        spacing_x = 60
        spacing_y = 50
        start_x = 70
        start_y = 50
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.invaders.append(Invader(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.last_shot > 250:  # Limit shooting rate
                        bullet = Bullet(self.player.x + self.player.width // 2, self.player.y)
                        self.bullets.append(bullet)
                        self.last_shot = current_time
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
        return True

    def update(self):
        if self.game_over:
            return

        # Update player
        self.player.update()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)

        # Update invader bullets
        for bullet in self.invader_bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT:
                self.invader_bullets.remove(bullet)

        # Update invaders
        move_down = False
        for invader in self.invaders:
            invader.update()
            if invader.x <= 0 or invader.x >= SCREEN_WIDTH - invader.width:
                move_down = True

        if move_down:
            for invader in self.invaders:
                invader.drop_down()

        # Invader shooting
        current_time = pygame.time.get_ticks()
        if current_time - self.invader_shoot_timer > 1000 and self.invaders:
            shooting_invader = random.choice(self.invaders)
            bullet = Bullet(shooting_invader.x + shooting_invader.width // 2,
                            shooting_invader.y + shooting_invader.height, -1)
            self.invader_bullets.append(bullet)
            self.invader_shoot_timer = current_time

        # Check collisions
        self.check_collisions()

        # Check win condition
        if not self.invaders:
            self.level += 1
            self.create_invaders()
            # Increase difficulty
            global INVADER_SPEED
            INVADER_SPEED += 0.5

        # Check lose condition
        for invader in self.invaders:
            if invader.y + invader.height >= self.player.y:
                self.game_over = True

        if self.lives <= 0:
            self.game_over = True

    def check_collisions(self):
        # Player bullets hit invaders
        for bullet in self.bullets[:]:
            for invader in self.invaders[:]:
                if bullet.rect.colliderect(invader.rect):
                    self.bullets.remove(bullet)
                    self.invaders.remove(invader)
                    self.score += 10
                    break

        # Invader bullets hit player
        for bullet in self.invader_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                self.invader_bullets.remove(bullet)
                self.lives -= 1
                break

    def draw(self):
        self.screen.fill(BLACK)

        # Draw game objects
        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for bullet in self.invader_bullets:
            bullet.draw(self.screen)

        for invader in self.invaders:
            invader.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (10, 90))

        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()

    def restart_game(self):
        self.__init__()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

# Instructions text
instructions = """
Space Invaders Game Instructions:

Controls:
- Left/Right Arrow Keys: Move ship
- Spacebar: Shoot
- R: Restart game (when game over)

Objective:
- Destroy all invaders to advance to the next level
- Avoid invader bullets
- Don't let invaders reach the bottom

Features:
- Score system (10 points per invader)
- Lives system (3 lives)
- Progressive difficulty
- Level progression

Run the game:
"""

if __name__ == "__main__":
    print(instructions)
    game = Game()
    game.run()



class Game:
    def __init__(self):
        # ... existing code ...

        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)  # adjusted Y

        # ... rest unchanged ...

    def create_invaders(self):
        self.invaders = []
        rows = 5
        cols = 11
        spacing_x = 60
        spacing_y = 50
        start_x = 70
        start_y = 50
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.invaders.append(Invader(x, y))