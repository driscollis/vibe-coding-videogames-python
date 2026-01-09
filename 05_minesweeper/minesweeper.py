import pygame
import random

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700  # Added space for potential controls/info later

# Board dimensions
GRID_ROWS = 16
GRID_COLS = 16
CELL_SIZE = 35 # Size of each cell in pixels

# Game difficulty
NUM_MINES = 40

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
MAROON = (128, 0, 0)
TEAL = (0, 128, 128)

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")
font = pygame.font.Font(None, 36) # Default font, size 36

# --- Game Board Data Structures ---
# board_layout: Stores the actual values of cells (-1 for mine, 0-8 for adjacent mines)
# revealed_cells: Boolean grid, True if cell is revealed, False otherwise
# flagged_cells: Boolean grid, True if cell is flagged, False otherwise
board_layout = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
revealed_cells = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
flagged_cells = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

game_over = False
game_won = False
first_click = True # To ensure first click never lands on a mine

# --- Functions ---

def initialize_board(first_click_row, first_click_col):
    """
    Initializes the board with mines and calculates adjacent mine counts.
    Ensures the first clicked cell and its immediate neighbors are not mines.
    """
    global board_layout, revealed_cells, flagged_cells, game_over, game_won, first_click

    board_layout = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    revealed_cells = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    flagged_cells = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    game_over = False
    game_won = False
    first_click = False # Reset for subsequent games

    # Place mines
    mines_placed = 0
    while mines_placed < NUM_MINES:
        row = random.randint(0, GRID_ROWS - 1)
        col = random.randint(0, GRID_COLS - 1)

        # Ensure no mine is placed at the first click location or its 8 neighbors
        is_safe_zone = False
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if (0 <= first_click_row + dr < GRID_ROWS and
                    0 <= first_click_col + dc < GRID_COLS and
                    row == first_click_row + dr and
                    col == first_click_col + dc):
                    is_safe_zone = True
                    break
            if is_safe_zone:
                break

        if board_layout[row][col] != -1 and not is_safe_zone:
            board_layout[row][col] = -1 # -1 signifies a mine
            mines_placed += 1

    # Calculate numbers for non-mine cells
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if board_layout[r][c] == -1: # It's a mine, skip
                continue

            count = 0
            # Check all 8 neighbors
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: # Skip the cell itself
                        continue
                    nr, nc = r + dr, c + dc # Neighbor row, neighbor column
                    if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                        if board_layout[nr][nc] == -1: # Neighbor is a mine
                            count += 1
            board_layout[r][c] = count # Store the count

def draw_board():
    """Draws the current state of the game board."""
    screen.fill(BLACK) # Clear the screen before drawing

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cell_rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            # Draw the cell background
            pygame.draw.rect(screen, LIGHT_GRAY, cell_rect)
            pygame.draw.rect(screen, DARK_GRAY, cell_rect, 1) # Border

            if revealed_cells[r][c]:
                # Draw revealed cell content
                if board_layout[r][c] == -1:
                    # Draw a mine (red circle)
                    pygame.draw.circle(screen, RED, cell_rect.center, CELL_SIZE // 3)
                elif board_layout[r][c] > 0:
                    # Draw the number of adjacent mines
                    number = board_layout[r][c]
                    # Assign different colors for different numbers for better visibility
                    number_colors = {
                        1: BLUE, 2: GREEN, 3: RED, 4: DARK_BLUE,
                        5: MAROON, 6: TEAL, 7: BLACK, 8: GRAY
                    }
                    text_color = number_colors.get(number, BLACK)
                    text_surface = font.render(str(number), True, text_color)
                    text_rect = text_surface.get_rect(center=cell_rect.center)
                    screen.blit(text_surface, text_rect)
            elif flagged_cells[r][c]:
                # Draw a flag (green triangle)
                pygame.draw.polygon(screen, GREEN, [
                    (cell_rect.centerx, cell_rect.top + CELL_SIZE // 4),
                    (cell_rect.centerx - CELL_SIZE // 4, cell_rect.centery + CELL_SIZE // 4),
                    (cell_rect.centerx + CELL_SIZE // 4, cell_rect.centery + CELL_SIZE // 4)
                ])
                pygame.draw.line(screen, DARK_GRAY, cell_rect.center,
                                 (cell_rect.centerx, cell_rect.bottom - CELL_SIZE // 4), 2)

    # Display game status
    status_text = ""
    if game_over:
        status_text = "Game Over! You hit a mine!"
    elif game_won:
        status_text = "Congratulations! You won!"

    if status_text:
        status_surface = font.render(status_text, True, WHITE)
        status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(status_surface, status_rect)

def reveal_cell(row, col):
    """
    Reveals a cell. If it's a 0, recursively reveals neighbors.
    Checks for win/loss conditions.
    """
    global game_over, game_won

    if not (0 <= row < GRID_ROWS and 0 <= col < GRID_COLS) or \
       revealed_cells[row][col] or flagged_cells[row][col]:
        return # Cell already revealed, flagged, or out of bounds

    revealed_cells[row][col] = True

    if board_layout[row][col] == -1:
        game_over = True # Game lost, you hit a mine
        # Reveal all mines when game is over
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if board_layout[r][c] == -1:
                    revealed_cells[r][c] = True
        return

    # If it's an empty cell (0), recursively reveal neighbors
    if board_layout[row][col] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                reveal_cell(row + dr, col + dc)

    check_win_condition()

def check_win_condition():
    """Checks if the player has won the game."""
    global game_won
    unrevealed_non_mines = 0
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if not revealed_cells[r][c] and board_layout[r][c] != -1:
                unrevealed_non_mines += 1
    if unrevealed_non_mines == 0:
        game_won = True
        # If won, reveal all remaining flags (mines) as a visual cue
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if board_layout[r][c] == -1:
                    flagged_cells[r][c] = True


# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over or game_won:
                # If game is over/won, a click restarts the game
                initialize_board(-1, -1) # Reset with dummy safe zone, new game will be first click
                first_click = True
                continue

            mouse_x, mouse_y = event.pos
            # Calculate grid coordinates based on mouse position
            col = mouse_x // CELL_SIZE
            row = mouse_y // CELL_SIZE

            # Ensure click is within the grid boundaries
            if not (0 <= row < GRID_ROWS and 0 <= col < GRID_COLS):
                continue

            if event.button == 1:  # Left click
                if first_click:
                    # On the very first click, initialize the board ensuring
                    # the clicked cell is safe
                    initialize_board(row, col)
                    reveal_cell(row, col) # Reveal the first clicked cell
                else:
                    reveal_cell(row, col)
            elif event.button == 3: # Right click
                # Toggle flag if the cell is not already revealed
                if not revealed_cells[row][col]:
                    flagged_cells[row][col] = not flagged_cells[row][col]

    # Drawing
    draw_board()

    # Update the display
    pygame.display.flip()

pygame.quit()