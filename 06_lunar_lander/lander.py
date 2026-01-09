import math
import sys
import random
import pygame
from dataclasses import dataclass
from enum import Enum, auto

# ---------------------------
# Config
# ---------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.12  # downward acceleration (px/s^2)
THRUST = 0.22   # main engine acceleration (px/s^2)
ROT_THRUST = 2.1  # degrees/frame
FUEL_BURN_MAIN = 0.35  # units/frame when main engine is on
FUEL_BURN_RCS = 0.06   # units/frame when rotating
MAX_LANDING_SPEED = 1.4  # max |vx| and vy for safe landing
MAX_LANDING_ANGLE = 8.0  # degrees from upright allowed
START_FUEL = 100.0
PAD_COUNT = 3
TERRAIN_ROUGHNESS = 0.3

# Colors
WHITE = (240, 240, 240)
BLACK = (12, 12, 16)
ORANGE = (255, 170, 50)
RED = (235, 70, 70)
GREEN = (40, 210, 110)
BLUE = (90, 180, 255)
GRAY = (80, 90, 100)
DARK_GRAY = (45, 50, 60)
YELLOW = (255, 230, 120)

# ---------------------------
# Data types
# ---------------------------
@dataclass
class Lander:
    x: float
    y: float
    vx: float
    vy: float
    angle: float  # degrees, 0 = up
    fuel: float
    alive: bool = True
    landed: bool = False

    def rect(self):
        return pygame.Rect(int(self.x) - 10, int(self.y) - 14, 20, 28)

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    CRASH = auto()
    LANDED = auto()

# ---------------------------
# Helpers
# ---------------------------
def wrap(value, limit):
    # keep lander on screen horizontally
    if value < 0:
        return value + limit
    if value >= limit:
        return value - limit
    return value

@dataclass
class Pad:
    x: int
    y: int
    w: int

# ---------------------------
# Terrain generation
# ---------------------------
def generate_terrain(width, height, pad_count=3):
    # Simple midpoint displacement / 1D fractal terrain
    points = [(0, int(height * 0.75)), (width, int(height * 0.75))]
    disp = height * TERRAIN_ROUGHNESS
    iters = 9
    for _ in range(iters):
        new_pts = [points[0]]
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            mx = (x1 + x2) // 2
            my = (y1 + y2) // 2 + random.randint(int(-disp), int(disp))
            my = max(int(height * 0.45), min(int(height * 0.92), my))
            new_pts.append((mx, my))
            new_pts.append(points[i + 1])
        points = new_pts
        disp *= 0.55

    # Make landing pads: flatten segments
    pads = []
    segments = []
    points.sort(key=lambda p: p[0])
    for i in range(len(points) - 1):
        segments.append((points[i], points[i + 1]))

    usable = [s for s in segments if s[1][0] - s[0][0] > 40]
    random.shuffle(usable)
    chosen = usable[:pad_count]

    for (a, b) in chosen:
        pad_center = (a[0] + b[0]) // 2
        width = random.randint(60, 120)
        x1 = max(0, pad_center - width // 2)
        x2 = min(WIDTH, pad_center + width // 2)
        y = (a[1] + b[1]) // 2
        # flatten nearby points to y
        for i, (px, py) in enumerate(points):
            if x1 <= px <= x2:
                points[i] = (px, y)
        pads.append(Pad(x1, y, x2 - x1))

    points.sort(key=lambda p: p[0])
    return points, pads

# ---------------------------
# Physics & game logic
# ---------------------------
def reset_game():
    lander = Lander(WIDTH * 0.2, HEIGHT * 0.15, 0.0, 0.0, 0.0, START_FUEL)
    terrain, pads = generate_terrain(WIDTH, HEIGHT, PAD_COUNT)
    score = 0
    time_alive = 0
    return lander, terrain, pads, score, time_alive


def update_lander(lander: Lander, keys):
    if not (lander.alive and not lander.landed):
        return {"main": False, "rcs_left": False, "rcs_right": False}

    thrusting = False
    rcs_left = False
    rcs_right = False

    # rotation (A/D or Left/Right)
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and lander.fuel > 0:
        lander.angle -= ROT_THRUST
        rcs_left = True
        lander.fuel = max(0.0, lander.fuel - FUEL_BURN_RCS)
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and lander.fuel > 0:
        lander.angle += ROT_THRUST
        rcs_right = True
        lander.fuel = max(0.0, lander.fuel - FUEL_BURN_RCS)

    # main engine (Up/W or Space)
    if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and lander.fuel > 0:
        # force vector based on angle
        rad = math.radians(lander.angle)
        ax = -math.sin(rad) * THRUST
        ay = -math.cos(rad) * THRUST
        lander.vx += ax
        lander.vy += ay
        thrusting = True
        lander.fuel = max(0.0, lander.fuel - FUEL_BURN_MAIN)

    # gravity
    lander.vy += GRAVITY

    # integrate
    lander.x = wrap(lander.x + lander.vx, WIDTH)
    lander.y += lander.vy

    return {"main": thrusting, "rcs_left": rcs_left, "rcs_right": rcs_right}


def check_collision(lander: Lander, terrain_points, pads):
    # Find terrain y directly below lander.x by segment interpolation
    # Get two surrounding points
    x = lander.x
    # binary search would be faster but list is small
    for i in range(len(terrain_points) - 1):
        (x1, y1), (x2, y2) = terrain_points[i], terrain_points[i + 1]
        if x1 <= x <= x2:
            t = (x - x1) / (x2 - x1) if x2 != x1 else 0
            ground_y = y1 + t * (y2 - y1)
            break
    else:
        ground_y = HEIGHT

    # contact?
    if lander.y + 14 >= ground_y:  # bottom of lander touches ground
        # determine if on a pad
        on_pad = None
        for pad in pads:
            if pad.x <= x <= pad.x + pad.w and abs(lander.y + 14 - pad.y) < 4:
                on_pad = pad
                break

        # landing criteria
        angle_ok = abs(((lander.angle + 180) % 360) - 180) <= MAX_LANDING_ANGLE
        speed_ok = abs(lander.vx) <= MAX_LANDING_SPEED and lander.vy <= MAX_LANDING_SPEED

        if on_pad and angle_ok and speed_ok:
            lander.landed = True
            lander.alive = True
            # snap to pad
            lander.y = on_pad.y - 14
            lander.vx = lander.vy = 0
            return 'landed', on_pad
        else:
            lander.alive = False
            lander.landed = False
            return 'crash', None

    return None, None


def compute_score(time_alive_frames, lander: Lander, pad: Pad | None):
    # Higher score for fuel left, gentle landing, smaller pad, and speed
    time_bonus = max(0, 2000 - time_alive_frames) // 2
    fuel_bonus = int(lander.fuel * 10)
    pad_bonus = 0
    if pad:
        pad_bonus = max(50, 300 - pad.w)
    return max(0, time_bonus + fuel_bonus + pad_bonus)

# ---------------------------
# Rendering
# ---------------------------
def draw_terrain(screen, terrain_points):
    # Fill sky
    screen.fill(BLACK)
    # Draw stars
    for _ in range(40):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, int(HEIGHT * 0.6))
        screen.set_at((x, y), WHITE)
    # Draw terrain polygon
    poly = terrain_points[:] + [(WIDTH, HEIGHT), (0, HEIGHT)]
    pygame.draw.polygon(screen, DARK_GRAY, poly)


def draw_pads(screen, pads):
    for p in pads:
        pygame.draw.rect(screen, BLUE, pygame.Rect(p.x, p.y - 3, p.w, 6), border_radius=3)
        # guidance lights
        for lx in range(p.x, p.x + p.w, 16):
            pygame.draw.circle(screen, YELLOW, (lx, p.y - 6), 2)


def draw_lander(screen, lander: Lander, thrust):
    # body as triangle + legs
    cx, cy = int(lander.x), int(lander.y)
    rad = math.radians(lander.angle)

    # Triangle points in local space (upright)
    pts = [
        (0, -12),  # top
        (-10, 10),
        (10, 10)
    ]
    # Rotate and translate
    rpts = []
    for px, py in pts:
        rx = px * math.cos(rad) - py * math.sin(rad)
        ry = px * math.sin(rad) + py * math.cos(rad)
        rpts.append((cx + int(rx), cy + int(ry)))

    pygame.draw.polygon(screen, WHITE, rpts, width=2)

    # Legs (fixed relative to body)
    for legx in (-8, 8):
        lx = legx * math.cos(rad) - 10 * math.sin(rad)
        ly = legx * math.sin(rad) + 10 * math.cos(rad)
        pygame.draw.line(screen, WHITE, (cx + int(lx), cy + int(ly)), (cx + int(lx*1.6), cy + int(ly + 10)), 2)

    # Flame when thrusting
    if thrust["main"] and lander.fuel > 0:
        fx = 0 * math.cos(rad) - 14 * math.sin(rad)
        fy = 0 * math.sin(rad) + 14 * math.cos(rad)
        jitter = random.randint(10, 18)
        base = (cx + int(fx), cy + int(fy))
        tip = (cx + int(fx - math.sin(rad) * jitter), cy + int(fy + math.cos(rad) * jitter))
        pygame.draw.line(screen, ORANGE, base, tip, 4)


def draw_hud(screen, font, small, lander: Lander, score, pads):
    text = [
        f"Fuel: {lander.fuel:05.1f}",
        f"VX: {lander.vx:+.2f}  VY: {lander.vy:+.2f}",
        f"Angle: {(((lander.angle + 180) % 360) - 180):+.1f}°",
        f"Score: {score}",
    ]
    for i, t in enumerate(text):
        surf = small.render(t, True, WHITE)
        screen.blit(surf, (10, 10 + i * 18))

    # draw target indicators for pads
    for pad in pads:
        pygame.draw.rect(screen, GRAY, pygame.Rect(pad.x, pad.y - 2, pad.w, 4), 1, border_radius=2)


def message_center(screen, font, lines, color=WHITE, y=HEIGHT//2):
    for i, line in enumerate(lines):
        surf = font.render(line, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, y + i * 40))
        screen.blit(surf, rect)

# ---------------------------
# Main
# ---------------------------
def main():
    pygame.init()
    pygame.display.set_caption("Lunar Lander (pygame)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 36)
    small = pygame.font.SysFont("consolas", 18)

    lander, terrain, pads, score, time_alive = reset_game()
    state = GameState.MENU
    last_pad = None

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if state in (GameState.CRASH, GameState.LANDED, GameState.MENU):
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        lander, terrain, pads, score, time_alive = reset_game()
                        state = GameState.PLAYING

        keys = pygame.key.get_pressed()

        # Update
        if state == GameState.MENU:
            pass
        elif state == GameState.PLAYING:
            thrust = update_lander(lander, keys)
            outcome, pad = check_collision(lander, terrain, pads)
            time_alive += 1
            if outcome == 'landed':
                gained = compute_score(time_alive, lander, pad)
                score += gained
                last_pad = pad
                state = GameState.LANDED
            elif outcome == 'crash' or lander.y > HEIGHT + 60:
                last_pad = None
                state = GameState.CRASH
            else:
                last_pad = None
        else:
            thrust = {"main": False, "rcs_left": False, "rcs_right": False}

        # Draw
        draw_terrain(screen, terrain)
        draw_pads(screen, pads)

        if state == GameState.MENU:
            title = ["LUNAR LANDER", "Press ENTER/SPACE to start"]
            message_center(screen, font, [title[0]], YELLOW, HEIGHT//2 - 40)
            message_center(screen, small, [title[1], "Controls: ←/→ rotate, ↑ or SPACE for thrust",
                                           f"Safe landing: |VX|≤{MAX_LANDING_SPEED}, VY≤{MAX_LANDING_SPEED}, |angle|≤{MAX_LANDING_ANGLE}°"], WHITE, HEIGHT//2 + 10)
        elif state == GameState.PLAYING:
            draw_lander(screen, lander, thrust)
            draw_hud(screen, font, small, lander, score, pads)
        elif state == GameState.CRASH:
            draw_lander(screen, lander, {"main": False, "rcs_left": False, "rcs_right": False})
            draw_hud(screen, font, small, lander, score, pads)
            message_center(screen, font, ["CRASH!", "Press R or ENTER to retry"], RED, HEIGHT//2 - 20)
        elif state == GameState.LANDED:
            draw_lander(screen, lander, {"main": False, "rcs_left": False, "rcs_right": False})
            draw_hud(screen, font, small, lander, score, pads)
            gained = compute_score(time_alive, lander, last_pad)
            message_center(screen, font, ["SUCCESS!", f"Score +{gained}", "Press R or ENTER for a new terrain"], GREEN, HEIGHT//2 - 20)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()