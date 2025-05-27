import pygame
import sys
import copy
import asyncio
import platform

pygame.init()

WIDTH, HEIGHT = 800, 1200
SQUARE_SIZE = WIDTH // 8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

THEMES = [
    [(255, 255, 0), (0, 128, 0)],
    [(255, 200, 150), (150, 100, 50)],
    [(200, 200, 255), (100, 100, 150)],
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

INITIAL_BOARD = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
]


def load_images():
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
    images = {}
    for piece in pieces:
        images[piece] = pygame.transform.scale(pygame.image.load(f'assets/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))
    return images


def draw_board(screen, theme):
    colors = THEMES[theme]
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


def draw_highlights(screen, moves):
    for move in moves:
        x, y = move[1]
        pygame.draw.circle(screen, (255, 0, 0),
                           (x * SQUARE_SIZE + SQUARE_SIZE // 2, y * SQUARE_SIZE + SQUARE_SIZE // 2), 10)


def draw_button(screen, text, x, y, w, h, color):
    pygame.draw.rect(screen, WHITE, (x, y, w, h), 2)
    pygame.draw.rect(screen, color, (x + 2, y + 2, w - 4, h - 4))
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(text_surf, text_rect)


def draw_ui(screen, game_phase, turn, white_time, black_time, paused, game_over, message, promoting, promote_pos,
            images):
    if game_phase == "pre_game":
        draw_button(screen, "10m", 300, 850, 100, 50, (100, 100, 100))
        draw_button(screen, "20m", 410, 850, 100, 50, (100, 100, 100))
        draw_button(screen, "30m", 520, 850, 100, 50, (100, 100, 100))
        draw_button(screen, "Start", 300, 920, 100, 50, (100, 100, 100))
    elif game_phase == "in_game":
        draw_button(screen, "Restart", 50, 850, 100, 50, (100, 100, 100))
        draw_button(screen, "Pause" if not paused else "Resume", 160, 850, 100, 50, (100, 100, 100))
        draw_button(screen, "Theme", 270, 850, 100, 50, (100, 100, 100))
        draw_button(screen, "Undo", 380, 850, 100, 50, (100, 100, 100))
        draw_button(screen, "Redo", 490, 850, 100, 50, (100, 100, 100))
        white_timer = font.render(f"White: {format_time(white_time)}", True, WHITE)
        black_timer = font.render(f"Black: {format_time(black_time)}", True, WHITE)
        screen.blit(white_timer, (600, 850))
        screen.blit(black_timer, (600, 920))
        if message:
            msg_text = font.render(message, True, WHITE)
            screen.blit(msg_text, (300, 920))
        if promoting:
            color = 'w' if promote_pos[1] == 0 else 'b'
            pieces = [color + 'Q', color + 'R', color + 'B', color + 'N']
            for i, piece in enumerate(pieces):
                screen.blit(images[piece], (300 + i * 100, 850))
        turn_text = font.render(f"{turn.upper()}'s Turn", True, WHITE)
        text_rect = turn_text.get_rect(center=(WIDTH // 2, 10))
        pygame.draw.rect(screen, BLACK, (text_rect.x - 5, text_rect.y - 5, text_rect.width + 10, text_rect.height + 10))
        screen.blit(turn_text, text_rect)


def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def get_square_under_mouse(mouse_pos):
    x, y = mouse_pos[0] // SQUARE_SIZE, mouse_pos[1] // SQUARE_SIZE
    return x, y


def handle_mouse_click(board, selected_piece, selected_pos, turn, promoting, promote_pos):
    x, y = get_square_under_mouse(pygame.mouse.get_pos())
    if selected_piece:
        attempted_move = (selected_pos, (x, y))
        selected_piece = None
        selected_pos = None
        return selected_piece, selected_pos, turn, promoting, promote_pos, attempted_move
    else:
        if board[y][x][0] == turn:
            selected_piece = board[y][x]
            selected_pos = (x, y)
        return selected_piece, selected_pos, turn, promoting, promote_pos, None


def is_valid_move(board, piece, start_pos, end_pos, turn):
    if piece == '--' or board[end_pos[1]][end_pos[0]][0] == turn:
        return False
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
    start_row = 6 if piece[0] == 'w' else 1
    if start_x == end_x and board[end_y][end_x] == '--':
        if end_y - start_y == direction:
            return True
        if start_y == start_row and end_y - start_y == 2 * direction and board[start_y + direction][start_x] == '--':
            return True
    if abs(start_x - end_x) == 1 and end_y - start_y == direction and board[end_y][end_x] != '--' and \
            board[end_y][end_x][0] != piece[0]:
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


def get_pseudo_legal_moves(board, player):
    moves = []
    for row in range(8):
        for col in range(8):
            if board[row][col][0] == player:
                piece = board[row][col]
                if piece[1] == 'P':
                    piece_moves = get_pawn_moves(board, col, row, player)
                elif piece[1] == 'R':
                    piece_moves = get_rook_moves(board, col, row, player)
                elif piece[1] == 'N':
                    piece_moves = get_knight_moves(board, col, row, player)
                elif piece[1] == 'B':
                    piece_moves = get_bishop_moves(board, col, row, player)
                elif piece[1] == 'Q':
                    piece_moves = get_queen_moves(board, col, row, player)
                elif piece[1] == 'K':
                    piece_moves = get_king_moves(board, col, row, player)
                else:
                    piece_moves = []
                for end_pos in piece_moves:
                    moves.append(((col, row), end_pos))
    return moves


def get_pawn_moves(board, col, row, color):
    moves = []
    direction = -1 if color == 'w' else 1
    start_row = 6 if color == 'w' else 1
    if 0 <= row + direction < 8 and board[row + direction][col] == '--':
        moves.append((col, row + direction))
        if row == start_row and board[row + 2 * direction][col] == '--' and board[row + direction][col] == '--':
            moves.append((col, row + 2 * direction))
    if col > 0 and 0 <= row + direction < 8 and board[row + direction][col - 1][0] == ('b' if color == 'w' else 'w'):
        moves.append((col - 1, row + direction))
    if col < 7 and 0 <= row + direction < 8 and board[row + direction][col + 1][0] == ('b' if color == 'w' else 'w'):
        moves.append((col + 1, row + direction))
    return moves


def get_rook_moves(board, col, row, color):
    moves = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        x, y = col + dx, row + dy
        while 0 <= x < 8 and 0 <= y < 8:
            if board[y][x] == '--':
                moves.append((x, y))
            elif board[y][x][0] != color:
                moves.append((x, y))
                break
            else:
                break
            x += dx
            y += dy
    return moves


def get_knight_moves(board, col, row, color):
    moves = []
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for dx, dy in knight_moves:
        x, y = col + dx, row + dy
        if 0 <= x < 8 and 0 <= y < 8 and (board[y][x] == '--' or board[y][x][0] != color):
            moves.append((x, y))
    return moves


def get_bishop_moves(board, col, row, color):
    moves = []
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in directions:
        x, y = col + dx, row + dy
        while 0 <= x < 8 and 0 <= y < 8:
            if board[y][x] == '--':
                moves.append((x, y))
            elif board[y][x][0] != color:
                moves.append((x, y))
                break
            else:
                break
            x += dx
            y += dy
    return moves


def get_queen_moves(board, col, row, color):
    return get_rook_moves(board, col, row, color) + get_bishop_moves(board, col, row, color)


def get_king_moves(board, col, row, color):
    moves = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            x, y = col + dx, row + dy
            if 0 <= x < 8 and 0 <= y < 8 and (board[y][x] == '--' or board[y][x][0] != color):
                moves.append((x, y))
    return moves


def find_king_position(board, player):
    for row in range(8):
        for col in range(8):
            if board[row][col] == player + 'K':
                return (col, row)
    return None


def is_in_check(board, player):
    king_pos = find_king_position(board, player)
    if not king_pos:
        return False
    opponent = 'b' if player == 'w' else 'w'
    opponent_moves = get_pseudo_legal_moves(board, opponent)
    return any(move[1] == king_pos for move in opponent_moves)


def get_all_legal_moves(board, player):
    pseudo_moves = get_pseudo_legal_moves(board, player)
    legal_moves = []
    for start_pos, end_pos in pseudo_moves:
        temp_board = copy.deepcopy(board)
        temp_board[end_pos[1]][end_pos[0]] = temp_board[start_pos[1]][start_pos[0]]
        temp_board[start_pos[1]][start_pos[0]] = '--'
        if temp_board[end_pos[1]][end_pos[0]][1] == 'P' and (end_pos[1] == 0 or end_pos[1] == 7):
            temp_board[end_pos[1]][end_pos[0]] = player + 'Q'
        if not is_in_check(temp_board, player):
            legal_moves.append((start_pos, end_pos))
    return legal_moves


def reset_game():
    global board, turn, selected_piece, selected_pos, history, redo_stack, white_time, black_time, game_over, message, promoting
    board = copy.deepcopy(INITIAL_BOARD)
    turn = 'w'
    selected_piece = None
    selected_pos = None
    history = []
    redo_stack = []
    white_time = time_control
    black_time = time_control
    game_over = False
    message = ""
    promoting = False


board = copy.deepcopy(INITIAL_BOARD)
selected_piece = None
selected_pos = None
turn = 'w'
history = []
redo_stack = []
time_control = 600
white_time = time_control
black_time = time_control
paused = False
game_over = False
message = ""
promoting = False
promote_pos = None
theme = 0
game_phase = "pre_game"
promotion_options = [(300, 850), (400, 850), (500, 850), (600, 850)]


async def main():
    global board, selected_piece, selected_pos, turn, paused, game_over, message, promoting, promote_pos, theme, time_control, white_time, black_time, game_phase
    images = load_images()
    while True:
        delta = clock.tick(FPS) / 1000.0
        if game_phase == "in_game" and not paused and not game_over and not promoting:
            if turn == 'w':
                white_time -= delta
                if white_time <= 0:
                    white_time = 0
                    game_over = True
                    message = "Time's up! Black wins!"
            else:
                black_time -= delta
                if black_time <= 0:
                    black_time = 0
                    game_over = True
                    message = "Time's up! White wins!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if game_phase == "pre_game":
                    x, y = mouse_pos
                    if 300 <= x <= 400 and 850 <= y <= 900:
                        time_control = 600
                    elif 410 <= x <= 510 and 850 <= y <= 900:
                        time_control = 1200
                    elif 520 <= x <= 620 and 850 <= y <= 900:
                        time_control = 1800
                    elif 300 <= x <= 400 and 920 <= y <= 970:
                        reset_game()
                        game_phase = "in_game"
                elif game_phase == "in_game":
                    if promoting:
                        for i, (px, py) in enumerate(promotion_options):
                            if px <= mouse_pos[0] < px + SQUARE_SIZE and py <= mouse_pos[1] < py + SQUARE_SIZE:
                                promo_type = ['Q', 'R', 'B', 'N'][i]
                                color = 'w' if promote_pos[1] == 0 else 'b'
                                board[promote_pos[1]][promote_pos[0]] = color + promo_type
                                promoting = False
                                turn = 'b' if turn == 'w' else 'w'
                                if is_in_check(board, turn):
                                    message = "Check"
                                    legal_moves = get_all_legal_moves(board, turn)
                                    if not legal_moves:
                                        winner = "White" if turn == 'b' else "Black"
                                        message = f"Checkmate! {winner} wins!"
                                        game_over = True
                                else:
                                    message = ""
                                    legal_moves = get_all_legal_moves(board, turn)
                                    if not legal_moves:
                                        message = "Stalemate! Draw!"
                                        game_over = True
                                break
                    else:
                        if mouse_pos[1] < 800 and not game_over and not paused:
                            selected_piece, selected_pos, turn, promoting, promote_pos, attempted_move = handle_mouse_click(
                                board, selected_piece, selected_pos, turn, promoting, promote_pos)
                            if attempted_move:
                                legal_moves = get_all_legal_moves(board, turn)
                                if attempted_move in legal_moves:
                                    start_pos, end_pos = attempted_move
                                    history.append((copy.deepcopy(board), turn))
                                    board[end_pos[1]][end_pos[0]] = board[start_pos[1]][start_pos[0]]
                                    board[start_pos[1]][start_pos[0]] = '--'
                                    if board[end_pos[1]][end_pos[0]][1] == 'P' and (end_pos[1] == 0 or end_pos[1] == 7):
                                        promoting = True
                                        promote_pos = end_pos
                                    else:
                                        turn = 'b' if turn == 'w' else 'w'
                                        if is_in_check(board, turn):
                                            message = "Check"
                                            legal_moves = get_all_legal_moves(board, turn)
                                            if not legal_moves:
                                                winner = "White" if turn == 'b' else "Black"
                                                message = f"Checkmate! {winner} wins!"
                                                game_over = True
                                        else:
                                            message = ""
                                            legal_moves = get_all_legal_moves(board, turn)
                                            if not legal_moves:
                                                message = "Stalemate! Draw!"
                                                game_over = True
                        if mouse_pos[1] >= 800:
                            x, y = mouse_pos
                            if 50 <= x <= 150 and 850 <= y <= 900:
                                reset_game()
                            elif 160 <= x <= 260 and 850 <= y <= 900:
                                paused = not paused
                            elif 270 <= x <= 370 and 850 <= y <= 900:
                                theme = (theme + 1) % len(THEMES)
                            elif 380 <= x <= 480 and 850 <= y <= 900 and history:
                                redo_stack.append((copy.deepcopy(board), turn))
                                board, turn = history.pop()
                                selected_piece = None
                                selected_pos = None
                            elif 490 <= x <= 590 and 850 <= y <= 900 and redo_stack:
                                history.append((copy.deepcopy(board), turn))
                                board, turn = redo_stack.pop()
                                selected_piece = None
                                selected_pos = None

        screen.fill(BLACK)
        if game_phase in ["pre_game", "in_game"]:
            draw_board(screen, theme)
            draw_pieces(screen, board, images)
        if game_phase == "in_game" and selected_pos:
            moves = [move for move in get_all_legal_moves(board, turn) if move[0] == selected_pos]
            draw_highlights(screen, moves)
        draw_ui(screen, game_phase, turn, white_time, black_time, paused, game_over, message, promoting, promote_pos,
                images)
        pygame.display.flip()
        await asyncio.sleep(1.0 / FPS)


if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
