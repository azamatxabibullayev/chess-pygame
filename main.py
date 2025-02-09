import pygame
import sys


pygame.init()


WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8
YELLOW = (255, 255, 0)
GREEN = (0, 128, 0)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")


def load_images():
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
    images = {}
    for piece in pieces:
        images[piece] = pygame.transform.scale(pygame.image.load(f'assets/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))
    return images


def draw_board(screen):
    colors = [YELLOW, GREEN]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board, images):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != '--':
                screen.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))


def get_square_under_mouse():
    mouse_pos = pygame.mouse.get_pos()
    x, y = mouse_pos[0] // SQUARE_SIZE, mouse_pos[1] // SQUARE_SIZE
    return x, y


def handle_mouse_click(board, selected_piece, selected_pos, turn):
    x, y = get_square_under_mouse()
    if selected_piece:
        if is_valid_move(board, selected_piece, selected_pos, (x, y), turn):
            board[y][x] = selected_piece
            board[selected_pos[1]][selected_pos[0]] = '--'
            selected_piece = None
            selected_pos = None
            turn = 'b' if turn == 'w' else 'w'
        else:
            selected_piece = None
            selected_pos = None
    else:
        if board[y][x][0] == turn:
            selected_piece = board[y][x]
            selected_pos = (x, y)
    return selected_piece, selected_pos, turn


def is_valid_move(board, piece, start_pos, end_pos, turn):
    if piece == '--':
        return False
    if board[end_pos[1]][end_pos[0]][0] == turn:
        return False

    start_x, start_y = start_pos
    end_x, end_y = end_pos
    piece_type = piece[1]

    if piece_type == 'P':
        return is_valid_pawn_move(board, piece, start_pos, end_pos)
    elif piece_type == 'R':
        return is_valid_rook_move(board, start_pos, end_pos)
    elif piece_type == 'N':
        return is_valid_knight_move(start_pos, end_pos)
    elif piece_type == 'B':
        return is_valid_bishop_move(board, start_pos, end_pos)
    elif piece_type == 'Q':
        return is_valid_queen_move(board, start_pos, end_pos)
    elif piece_type == 'K':
        return is_valid_king_move(start_pos, end_pos)

    return False


def is_valid_pawn_move(board, piece, start_pos, end_pos):
    direction = -1 if piece[0] == 'w' else 1
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    if start_x == end_x and board[end_y][end_x] == '--' and ((end_y - start_y == direction) or (start_y == 1 and end_y - start_y == 2 * direction) or (start_y == 6 and end_y - start_y == 2 * direction)):
        return True
    if abs(start_x - end_x) == 1 and end_y - start_y == direction and board[end_y][end_x] != '--' and board[end_y][end_x][0] != piece[0]:
        return True
    return False


def is_valid_rook_move(board, start_pos, end_pos):
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    if start_x != end_x and start_y != end_y:
        return False
    step_x = 0 if start_x == end_x else (1 if end_x > start_x else -1)
    step_y = 0 if start_y == end_y else (1 if end_y > start_y else -1)
    current_x, current_y = start_x + step_x, start_y + step_y
    while (current_x, current_y) != (end_x, end_y):
        if board[current_y][current_x] != '--':
            return False
        current_x += step_x
        current_y += step_y
    return True


def is_valid_knight_move(start_pos, end_pos):
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    dx = abs(start_x - end_x)
    dy = abs(start_y - end_y)
    return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)


def is_valid_bishop_move(board, start_pos, end_pos):
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    if abs(start_x - end_x) != abs(start_y - end_y):
        return False
    step_x = 1 if end_x > start_x else -1
    step_y = 1 if end_y > start_y else -1
    current_x, current_y = start_x + step_x, start_y + step_y
    while (current_x, current_y) != (end_x, end_y):
        if board[current_y][current_x] != '--':
            return False
        current_x += step_x
        current_y += step_y
    return True


def is_valid_queen_move(board, start_pos, end_pos):
    return is_valid_rook_move(board, start_pos, end_pos) or is_valid_bishop_move(board, start_pos, end_pos)


def is_valid_king_move(start_pos, end_pos):
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    dx = abs(start_x - end_x)
    dy = abs(start_y - end_y)
    return max(dx, dy) == 1


board = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
]

selected_piece = None
selected_pos = None
turn = 'w'

def main():
    images = load_images()
    global selected_piece, selected_pos, turn

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                selected_piece, selected_pos, turn = handle_mouse_click(board, selected_piece, selected_pos, turn)

        draw_board(screen)
        draw_pieces(screen, board, images)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()