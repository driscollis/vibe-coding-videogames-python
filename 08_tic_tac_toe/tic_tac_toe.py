import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
RESTART_BUTTON_COLOR = (255, 255, 255)
RESTART_BUTTON_TEXT_COLOR = (0, 0, 0)

# Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe')

# Board
board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

# Font
font = pygame.font.SysFont('Arial', 40)

def draw_lines():
    # Horizontal lines
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    # Vertical lines
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR,
                                  (int(col * SQUARE_SIZE + SQUARE_SIZE // 2),
                                   int(row * SQUARE_SIZE + SQUARE_SIZE // 2)),
                                  CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 'X':
                pygame.draw.line(screen, CROSS_COLOR,
                                (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE),
                                CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                                (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                                (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                CROSS_WIDTH)

def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] is None

def is_board_full():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                return False
    return True

def check_win(player):
    # Vertical win check
    for col in range(BOARD_COLS):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            return True
    # Horizontal win check
    for row in range(BOARD_ROWS):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            return True
    # Diagonal win check
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        return True
    if board[0][2] == player and board[1][1] == player and board[2][0] == player:
        return True
    return False

def draw_restart_button():
    button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 50, 200, 40)
    pygame.draw.rect(screen, RESTART_BUTTON_COLOR, button_rect)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
    text = font.render('Restart', True, RESTART_BUTTON_TEXT_COLOR)
    screen.blit(text, (button_rect.centerx - text.get_width() // 2, button_rect.centery - text.get_height() // 2))
    return button_rect

def draw_winner(player):
    if player == 'X':
        text = font.render('X wins!', True, CROSS_COLOR)
    elif player == 'O':
        text = font.render('O wins!', True, CIRCLE_COLOR)
    else:
        text = font.render('Tie!', True, (0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

def restart_game():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = None

def main():
    player = 'X'
    game_over = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouseX, mouseY = event.pos
                clicked_row = mouseY // SQUARE_SIZE
                clicked_col = mouseX // SQUARE_SIZE

                if available_square(clicked_row, clicked_col):
                    mark_square(clicked_row, clicked_col, player)
                    if check_win(player):
                        game_over = True
                    elif is_board_full():
                        game_over = True
                    else:
                        player = 'O' if player == 'X' else 'X'

            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                mouseX, mouseY = event.pos
                button_rect = draw_restart_button()
                if button_rect.collidepoint(mouseX, mouseY):
                    restart_game()
                    player = 'X'
                    game_over = False

        screen.fill(BG_COLOR)
        draw_lines()
        draw_figures()
        if game_over:
            if check_win('X'):
                draw_winner('X')
            elif check_win('O'):
                draw_winner('O')
            else:
                draw_winner(None)
            button_rect = draw_restart_button()

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()