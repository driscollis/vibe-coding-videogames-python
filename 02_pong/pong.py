import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_SPEED_X = 6
BALL_SPEED_Y = 6

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move_up(self):
        if self.rect.top > 0:
            self.rect.y -= self.speed

    def move_down(self):
        if self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SIZE, BALL_SIZE)
        self.reset_ball()

    def reset_ball(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off top and bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y = -self.speed_y

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Game")
        self.clock = pygame.time.Clock()

        # Create game objects
        self.left_paddle = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.right_paddle = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()

        # Scores
        self.left_score = 0
        self.right_score = 0
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

        # Game state
        self.game_state = "menu"  # "menu", "playing", "paused"

    def handle_collision(self):
        # Ball collision with paddles
        if self.ball.rect.colliderect(self.left_paddle.rect):
            if self.ball.speed_x < 0:  # Only bounce if moving toward paddle
                self.ball.speed_x = -self.ball.speed_x
                # Add some variation based on where ball hits paddle
                hit_pos = (self.ball.rect.centery - self.left_paddle.rect.centery
                           ) / (PADDLE_HEIGHT / 2)
                self.ball.speed_y += hit_pos * 2

        if self.ball.rect.colliderect(self.right_paddle.rect):
            if self.ball.speed_x > 0:  # Only bounce if moving toward paddle
                self.ball.speed_x = -self.ball.speed_x
                # Add some variation based on where ball hits paddle
                hit_pos = (self.ball.rect.centery - self.right_paddle.rect.centery
                           ) / (PADDLE_HEIGHT / 2)
                self.ball.speed_y += hit_pos * 2

        # Limit ball speed
        max_speed = 12
        if abs(self.ball.speed_y) > max_speed:
            self.ball.speed_y = max_speed if self.ball.speed_y > 0 else -max_speed

    def check_scoring(self):
        # Check if ball went off screen
        if self.ball.rect.left <= 0:
            self.right_score += 1
            self.ball.reset_ball()
        elif self.ball.rect.right >= SCREEN_WIDTH:
            self.left_score += 1
            self.ball.reset_ball()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if self.game_state == "playing":
            # Left paddle controls (W/S)
            if keys[pygame.K_w]:
                self.left_paddle.move_up()
            if keys[pygame.K_s]:
                self.left_paddle.move_down()

            # Right paddle controls (UP/DOWN arrows)
            if keys[pygame.K_UP]:
                self.right_paddle.move_up()
            if keys[pygame.K_DOWN]:
                self.right_paddle.move_down()

    def draw_menu(self):
        self.screen.fill(BLACK)

        title_text = self.font.render("PONG", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        start_text = self.small_font.render("Press SPACE to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(start_text, start_rect)

        controls_text = [
            "Controls:",
            "Left Player: W (Up) / S (Down)",
            "Right Player: Arrow Keys",
            "Press R to restart during game",
            "Press ESC to return to menu"
        ]

        for i, text in enumerate(controls_text):
            rendered_text = self.small_font.render(text, True, GRAY if i == 0 else WHITE)
            text_rect = rendered_text.get_rect(center=(SCREEN_WIDTH // 2, 320 + i * 40))
            self.screen.blit(rendered_text, text_rect)

    def draw_game(self):
        self.screen.fill(BLACK)

        # Draw center line
        for i in range(0, SCREEN_HEIGHT, 20):
            if i % 40 == 0:
                pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 2, i, 4, 10))

        # Draw paddles and ball
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)
        self.ball.draw(self.screen)

        # Draw scores
        left_score_text = self.font.render(str(self.left_score), True, WHITE)
        right_score_text = self.font.render(str(self.right_score), True, WHITE)

        self.screen.blit(left_score_text, (SCREEN_WIDTH // 4, 50))
        self.screen.blit(right_score_text, (3 * SCREEN_WIDTH // 4 - right_score_text.get_width(), 50))

        # Draw instructions
        instruction_text = self.small_font.render("Press ESC for menu, R to restart", True, GRAY)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(instruction_text, instruction_rect)

    def reset_game(self):
        self.left_score = 0
        self.right_score = 0
        self.ball.reset_ball()
        self.left_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_state == "menu":
                        self.game_state = "playing"
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"
                    elif event.key == pygame.K_r and self.game_state == "playing":
                        self.reset_game()

            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "playing":
                self.handle_input()
                self.ball.move()
                self.handle_collision()
                self.check_scoring()
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PongGame()
    game.run()