import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
RED = (255, 0, 0)
HIGHLIGHT = (0, 255, 0)  # Green for valid moves

# Initialize piece images
PIECES = {
    'wp': 'images/wp.png', 'wn': 'images/wN.png', 'wb': 'images/wB.png', 'wr': 'images/wR.png', 'wq': 'images/wQ.png', 'wk': 'images/wK.png',
    'bp': 'images/bp.png', 'bn': 'images/bN.png', 'bb': 'images/bB.png', 'br': 'images/bR.png', 'bq': 'images/bQ.png', 'bk': 'images/bK.png',
}

# Directions for piece movement
DIRECTIONS = {
    'n': (-1, 0), 's': (1, 0), 'e': (0, 1), 'w': (0, -1),
    'ne': (-1, 1), 'nw': (-1, -1), 'se': (1, 1), 'sw': (1, -1)
}

# Initialize board setup
def initialize_board():
    return [
        ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
        ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
        ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
    ]

# Draw the chessboard
def draw_board(screen, check_square=None, valid_moves=[]):
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            # Highlight valid moves
            if (row, col) in valid_moves:
                pygame.draw.rect(screen, HIGHLIGHT, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

            if check_square and (row, col) == check_square:
                pygame.draw.rect(screen, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

# Draw the pieces on the board using images
def draw_pieces(screen, board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                piece_image_path = PIECES.get(piece)
                if piece_image_path:
                    piece_image = pygame.image.load(piece_image_path)  # Load the image
                    piece_image = pygame.transform.scale(piece_image, (SQUARE_SIZE, SQUARE_SIZE))  # Resize image to fit the square
                    screen.blit(piece_image, (col * SQUARE_SIZE, row * SQUARE_SIZE))  # Draw the image on the board

# Check if a position is on the board
def on_board(row, col):
    return 0 <= row < 8 and 0 <= col < 8

# Generate valid moves for a piece
def generate_moves(board, row, col):
    piece = board[row][col]
    if not piece:
        return []
    moves = []
    player = piece[0]
    kind = piece[1]

    if kind == 'p':  # Pawn
        direction = -1 if player == 'w' else 1
        start_row = 6 if player == 'w' else 1
        # Move forward
        if on_board(row + direction, col) and not board[row + direction][col]:
            moves.append((row + direction, col))
            # Double move on first move
            if row == start_row and not board[row + 2 * direction][col]:
                moves.append((row + 2 * direction, col))
        # Capture diagonally
        for dc in [-1, 1]:
            if on_board(row + direction, col + dc) and board[row + direction][col + dc]:
                if board[row + direction][col + dc][0] != player:
                    moves.append((row + direction, col + dc))

    elif kind == 'n':  # Knight
        knight_moves = [
            (row + 2, col + 1), (row + 2, col - 1), (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2), (row - 1, col + 2), (row - 1, col - 2)
        ]
        for r, c in knight_moves:
            if on_board(r, c) and (not board[r][c] or board[r][c][0] != player):
                moves.append((r, c))

    elif kind in 'rbq':  # Rook, Bishop, Queen
        directions = []
        if kind in 'rq':
            directions += ['n', 's', 'e', 'w']
        if kind in 'bq':
            directions += ['ne', 'nw', 'se', 'sw']

        for d in directions:
            dr, dc = DIRECTIONS[d]
            r, c = row + dr, col + dc
            while on_board(r, c):
                if not board[r][c]:
                    moves.append((r, c))
                elif board[r][c][0] != player:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

    elif kind == 'k':  # King
        for d in DIRECTIONS.values():
            r, c = row + d[0], col + d[1]
            if on_board(r, c) and (not board[r][c] or board[r][c][0] != player):
                moves.append((r, c))

    return moves

# Check if the player is in check
def is_in_check(board, player):
    king_pos = None
    for row in range(8):
        for col in range(8):
            if board[row][col] == player + 'k':
                king_pos = (row, col)
                break
    if not king_pos:
        return False

    opponent = 'b' if player == 'w' else 'w'
    for row in range(8):
        for col in range(8):
            if board[row][col] and board[row][col][0] == opponent:
                if king_pos in generate_moves(board, row, col):
                    return True
    return False

def find_king(board, color):
    """
    Finds the position of the king for a given color on the board.
    
    Args:
        board (list of lists): The current chess board.
        color (str): The color of the king to find ('w' for white, 'b' for black).

    Returns:
        tuple: The (row, col) position of the king.
    """
    king_symbol = f"{color}K"
    for row in range(8):
        for col in range(8):
            if board[row][col] == king_symbol:
                return (row, col)
    return None


# Check if there are any valid moves for the player
def has_valid_moves(board, player):
    for row in range(8):
        for col in range(8):
            if board[row][col] and board[row][col][0] == player:
                for move in generate_moves(board, row, col):
                    new_board = [row[:] for row in board]
                    new_board[move[0]][move[1]] = new_board[row][col]
                    new_board[row][col] = None
                    if not is_in_check(new_board, player):
                        return True
    return False

# Main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess - Two Player")
    
    board = initialize_board()
    selected_square = None
    current_player = 'w'  # 'w' for white, 'b' for black
    check_square = None
    valid_moves = []

    running = True
    while running:
        screen.fill(BLACK)
        draw_board(screen, check_square, valid_moves)
        draw_pieces(screen, board)  # Draw the pieces as images
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col, row = x // SQUARE_SIZE, y // SQUARE_SIZE

                if selected_square:
                    start_row, start_col = selected_square
                    piece = board[start_row][start_col]
                    if piece and piece[0] == current_player:
                        if (row, col) in generate_moves(board, start_row, start_col):
                            board[row][col] = piece
                            board[start_row][start_col] = None

                            if is_in_check(board, current_player):
                                print("Illegal move, still in check!")
                                board[start_row][start_col] = piece
                                board[row][col] = None
                            else:
                                if is_in_check(board, 'b' if current_player == 'w' else 'w'):
                                    check_square = find_king(board, 'b' if current_player == 'w' else 'w')
                                else:
                                    check_square = None

                                if not has_valid_moves(board, 'b' if current_player == 'w' else 'w'):
                                    if is_in_check(board, 'b' if current_player == 'w' else 'w'):
                                        print(f"Checkmate! {current_player} wins!")
                                    else:
                                        print("Stalemate!")
                                    running = False

                                current_player = 'b' if current_player == 'w' else 'w'
                    selected_square = None
                else:
                    if board[row][col] and board[row][col][0] == current_player:
                        selected_square = (row, col)
                        # Generate valid moves for the selected piece
                        valid_moves = generate_moves(board, row, col)  # Store valid moves here

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
