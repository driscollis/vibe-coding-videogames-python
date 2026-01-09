import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAPTION = "Python Pygame Asteroids"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Utility Functions ---

def distance(pos1, pos2):
    """Calculates the distance between two pygame Vector2 positions."""
    return (pos1 - pos2).length()

def wrap_position(position, surface):
    """Wraps an object's position around the screen edges."""
    x, y = position
    w, h = surface.get_size()
    return pygame.math.Vector2(x % w, y % h)

# --- Base Game Object Class ---

class GameObject:
    """Base class for all interactive objects (Ship, Asteroid, Bullet)."""
    def __init__(self, position, velocity, radius, color):
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.color = color
        self.screen = pygame.display.get_surface()

    def move(self, dt):
        """Updates the object's position based on its velocity and time delta (dt)."""
        self.position += self.velocity * dt
        self.position = wrap_position(self.position, self.screen)

    def draw(self):
        """Draws a simple circle representation of the object."""
        pygame.draw.circle(self.screen, self.color, (int(self.position.x), int(self.position.y)), self.radius, 1)

    def collides_with(self, other_obj):
        """Checks for collision based on distance between centers and combined radii."""
        return distance(self.position, other_obj.position) < self.radius + other_obj.radius

# --- Ship Class ---

class Ship(GameObject):
    """The player controlled spaceship."""
    def __init__(self, position):
        super().__init__(position, pygame.math.Vector2(0, 0), 15, WHITE)
        self.direction = 0  # Angle in degrees (0 is up, 90 is right)
        self.rotation_speed = 250  # degrees per second
        self.acceleration = 150  # pixels per second squared
        self.max_speed = 300
        self.is_accelerating = False
        self.is_rotating_left = False
        self.is_rotating_right = False
        self.lives = 3
        self.respawn_timer = 0
        self.invulnerability_duration = 3.0  # seconds of invulnerability after respawn

    def update(self, dt):
        """Handle movement and physics."""
        self.handle_rotation(dt)
        self.handle_thrust(dt)
        self.move(dt)

        # Handle invulnerability timer
        if self.respawn_timer > 0:
            self.respawn_timer -= dt

    def handle_rotation(self, dt):
        """Rotates the ship based on input flags."""
        if self.is_rotating_left:
            self.direction += self.rotation_speed * dt
        if self.is_rotating_right:
            self.direction -= self.rotation_speed * dt
        self.direction %= 360

    def handle_thrust(self, dt):
        """Applies thrust in the current direction if accelerating."""
        if self.is_accelerating:
            # Calculate thrust vector (pointing in the direction of the ship)
            angle_rad = math.radians(self.direction - 90) # Adjust for Pygame's standard angle system (0 is right)
            thrust_vector = pygame.math.Vector2(math.cos(angle_rad), -math.sin(angle_rad)) * self.acceleration

            # Apply acceleration
            self.velocity += thrust_vector * dt

            # Limit max speed
            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)
        else:
            # Apply light friction/drag
            self.velocity *= 0.99 # Simple drag

    def draw(self):
        """Draws the ship as a triangle pointing in its current direction."""
        if self.respawn_timer > 0 and (int(self.respawn_timer * 10) % 2) == 0:
            # Flashing effect when invulnerable
            return

        # Calculate the points of the triangle based on position and direction
        angle_rad = math.radians(self.direction)
        points = []

        # Nose point (front of the ship)
        nose = self.position + pygame.math.Vector2(0, -self.radius * 1.5).rotate(-self.direction + 90)
        points.append(nose)

        # Right base point
        right_base = self.position + pygame.math.Vector2(-self.radius, self.radius).rotate(-self.direction + 90)
        points.append(right_base)

        # Left base point
        left_base = self.position + pygame.math.Vector2(self.radius, self.radius).rotate(-self.direction + 90)
        points.append(left_base)

        # Draw the triangle (ship outline)
        pygame.draw.polygon(self.screen, self.color, [(p.x, p.y) for p in points], 2)

        # Draw engine flame if accelerating
        if self.is_accelerating:
            flame_point1 = self.position + pygame.math.Vector2(self.radius * 0.7, self.radius * 1.5).rotate(-self.direction + 90)
            flame_point2 = self.position + pygame.math.Vector2(-self.radius * 0.7, self.radius * 1.5).rotate(-self.direction + 90)
            flame_tail = self.position + pygame.math.Vector2(0, self.radius * 2.5).rotate(-self.direction + 90)
            pygame.draw.polygon(self.screen, RED, [flame_point1, flame_point2, flame_tail])

    def reset(self):
        """Resets ship position, velocity, and starts invulnerability."""
        self.position = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = 0
        self.respawn_timer = self.invulnerability_duration

    def destroy(self):
        """Reduces lives and triggers reset if lives remain."""
        if self.respawn_timer <= 0:
            self.lives -= 1
            if self.lives > 0:
                self.reset()
            return True # Successfully destroyed
        return False # Invulnerable, not destroyed

    def shoot(self):
        """Creates a new bullet originating from the nose of the ship."""
        # Calculate bullet starting position and velocity
        angle_rad = math.radians(self.direction - 90)
        forward_vector = pygame.math.Vector2(math.cos(angle_rad), -math.sin(angle_rad))

        # Start bullet slightly ahead of the ship's nose
        start_pos = self.position + forward_vector * (self.radius * 1.5 + 5)

        # Bullet velocity is ship velocity + fixed speed in forward direction
        bullet_speed = 500
        bullet_velocity = self.velocity + forward_vector * bullet_speed

        return Bullet(start_pos, bullet_velocity)

# --- Bullet Class ---

class Bullet(GameObject):
    """The projectile fired by the ship."""
    def __init__(self, position, velocity):
        super().__init__(position, velocity, 3, WHITE)
        self.lifetime = 2.0  # seconds

    def update(self, dt):
        """Updates position and decreases lifetime."""
        self.move(dt)
        self.lifetime -= dt
        # Bullets do not wrap, they are removed when they leave the screen or lifetime expires
        x, y = self.position
        if not (0 <= x <= self.screen.get_width() and 0 <= y <= self.screen.get_height()):
            self.lifetime = 0 # Mark for removal if off-screen

# --- Asteroid Class ---

class Asteroid(GameObject):
    """An asteroid that breaks into smaller pieces."""
    # Sizes and associated radii
    SIZES = {
        3: 40,  # Large
        2: 25,  # Medium
        1: 15   # Small
    }
    COLORS = {
        3: (150, 150, 150),
        2: (120, 120, 120),
        1: (90, 90, 90)
    }

    def __init__(self, position, velocity, size_level):
        radius = self.SIZES.get(size_level, 15)
        color = self.COLORS.get(size_level, (90, 90, 90))
        super().__init__(position, velocity, radius, color)
        self.size_level = size_level
        self.rotation_speed = random.uniform(-60, 60) # degrees per second
        self.angle = random.uniform(0, 360)

    @classmethod
    def create_random(cls, screen_rect, size_level=3):
        """Creates an asteroid spawning randomly off-screen and moving towards center."""
        side = random.choice([0, 1, 2, 3]) # 0:top, 1:right, 2:bottom, 3:left

        if side == 0:  # Top
            start_pos = pygame.math.Vector2(random.randint(0, screen_rect.width), -cls.SIZES[size_level])
        elif side == 1: # Right
            start_pos = pygame.math.Vector2(screen_rect.width + cls.SIZES[size_level], random.randint(0, screen_rect.height))
        elif side == 2: # Bottom
            start_pos = pygame.math.Vector2(random.randint(0, screen_rect.width), screen_rect.height + cls.SIZES[size_level])
        else: # Left
            start_pos = pygame.math.Vector2(-cls.SIZES[size_level], random.randint(0, screen_rect.height))

        # Target center
        center = pygame.math.Vector2(screen_rect.center)
        direction = (center - start_pos).normalize()

        # Velocity depends on size (smaller moves faster)
        base_speed = 50
        speed = base_speed + (4 - size_level) * 30
        velocity = direction.rotate(random.uniform(-45, 45)) * speed

        return cls(start_pos, velocity, size_level)

    def update(self, dt):
        """Handles movement and rotation."""
        self.move(dt)
        self.angle += self.rotation_speed * dt
        self.angle %= 360

    def draw(self):
        """Draws the asteroid as a rough, angular shape."""
        num_points = 8
        base_points = []
        for i in range(num_points):
            angle = math.radians(i * (360 / num_points))
            # Vary the distance from the center slightly for a rough look
            dist_factor = random.uniform(0.8, 1.2) if self.size_level == 3 else 1.0
            x = math.cos(angle) * self.radius * dist_factor
            y = math.sin(angle) * self.radius * dist_factor
            base_points.append(pygame.math.Vector2(x, y))

        # Rotate and translate points for drawing
        rotated_points = []
        for point in base_points:
            rotated_point = point.rotate(self.angle) + self.position
            rotated_points.append((int(rotated_point.x), int(rotated_point.y)))

        pygame.draw.polygon(self.screen, self.color, rotated_points, 2)

    def break_apart(self):
        """Returns a list of 2 smaller asteroids if size_level > 1, otherwise an empty list."""
        new_asteroids = []
        next_size = self.size_level - 1

        if next_size >= 1:
            for _ in range(2):
                # New velocity is randomized from the parent's velocity
                new_velocity = self.velocity.rotate(random.uniform(-45, 45)) * 1.5
                new_asteroids.append(Asteroid(self.position.copy(), new_velocity, next_size))

        return new_asteroids

# --- Game Class ---

class AsteroidsGame:
    """Manages the main game loop, state, and objects."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.game_over = False
        self.reset_game()

    def reset_game(self):
        """Initializes or resets all game objects and state."""
        self.ship = Ship(pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.bullets = []
        self.asteroids = []
        self.score = 0
        self.level = 1
        self.game_over = False

        self.spawn_initial_asteroids()

    def spawn_initial_asteroids(self):
        """Spawns asteroids based on the current level."""
        num_asteroids = 4 + (self.level * 2)
        for _ in range(num_asteroids):
            self.asteroids.append(Asteroid.create_random(self.screen.get_rect(), size_level=3))

    def process_input(self):
        """Handles keyboard and game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Key Down Events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.ship.lives > 0 and not self.game_over:
                        self.bullets.append(self.ship.shoot())
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

            # Set continuous movement flags
            self.ship.is_accelerating = pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]
            self.ship.is_rotating_left = pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]
            self.ship.is_rotating_right = pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d]

    def update(self, dt):
        """Updates the state of all game objects."""
        if self.game_over:
            return

        # 1. Update Ship
        self.ship.update(dt)

        # 2. Update Bullets
        for bullet in self.bullets:
            bullet.update(dt)
        # Remove expired bullets
        self.bullets = [b for b in self.bullets if b.lifetime > 0]

        # 3. Update Asteroids
        for asteroid in self.asteroids:
            asteroid.update(dt)

        # 4. Handle Collisions
        self.handle_collisions()

        # 5. Check for Level Complete
        if not self.asteroids and self.ship.lives > 0:
            self.level += 1
            self.spawn_initial_asteroids()
            self.ship.reset() # Give the player a brief pause and invulnerability

    def handle_collisions(self):
        """Handles Bullet-Asteroid and Ship-Asteroid collisions."""

        # Bullet-Asteroid Collisions
        bullets_to_remove = set()
        new_asteroids = []

        for bullet in self.bullets:
            for asteroid in self.asteroids:
                if bullet.collides_with(asteroid):
                    bullets_to_remove.add(bullet)

                    # Asteroid breaks apart
                    new_asteroids.extend(asteroid.break_apart())

                    # Update score
                    if asteroid.size_level == 3: self.score += 20
                    elif asteroid.size_level == 2: self.score += 50
                    elif asteroid.size_level == 1: self.score += 100

                    # Mark asteroid for removal
                    asteroid.size_level = 0 # Mark as destroyed
                    break # Bullet can only hit one asteroid

        # Remove hit bullets
        self.bullets = [b for b in self.bullets if b not in bullets_to_remove]

        # Remove destroyed asteroids and add new smaller ones
        self.asteroids = [a for a in self.asteroids if a.size_level > 0]
        self.asteroids.extend(new_asteroids)

        # Ship-Asteroid Collisions
        if self.ship.respawn_timer <= 0:
            for asteroid in self.asteroids:
                if self.ship.collides_with(asteroid):
                    self.ship.destroy()
                    if self.ship.lives <= 0:
                        self.game_over = True
                    # Immediately mark asteroid for removal to prevent multiple collisions/hits
                    asteroid.size_level = 0
                    break
            # Re-clean up asteroids after ship collision
            self.asteroids = [a for a in self.asteroids if a.size_level > 0]


    def draw(self):
        """Renders all game objects and HUD."""
        self.screen.fill(BLACK)

        # Draw objects
        self.ship.draw()
        for bullet in self.bullets:
            bullet.draw()
        for asteroid in self.asteroids:
            asteroid.draw()

        # Draw HUD (Score, Lives, Level)
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))

        # Draw Lives (simple icons)
        for i in range(self.ship.lives):
            # Draw a small ship icon on the left
            x_offset = 10 + i * 30
            y_offset = 50
            points = [
                (x_offset, y_offset - 10),
                (x_offset - 8, y_offset + 10),
                (x_offset + 8, y_offset + 10)
            ]
            pygame.draw.polygon(self.screen, WHITE, points, 1)


        # Game Over Screen
        if self.game_over:
            self.draw_message("GAME OVER", "Press 'R' to Restart", WHITE)

        # Instructions / Start message
        if self.score == 0 and self.level == 1 and not self.ship.is_accelerating and not self.bullets and not self.game_over:
            self.draw_message("ASTEROIDS", "W/Up: Thrust | A/D/Left/Right: Rotate | Space: Shoot", GREEN, y_offset=-50)

        pygame.display.flip()

    def draw_message(self, title, subtitle, color, y_offset=0):
        """Helper to draw large centered messages."""
        title_font = pygame.font.Font(None, 72)
        title_surf = title_font.render(title, True, color)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + y_offset))
        self.screen.blit(title_surf, title_rect)

        subtitle_surf = self.font.render(subtitle, True, color)
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50 + y_offset))
        self.screen.blit(subtitle_surf, subtitle_rect)

    def run(self):
        """The main game loop."""
        self.running = True
        while self.running:
            # Calculate time delta (dt) for framerate independence
            dt = self.clock.tick(60) / 1000.0  # dt is now in seconds

            self.process_input()
            self.update(dt)
            self.draw()

        pygame.quit()

if __name__ == '__main__':
    game = AsteroidsGame()
    game.run()