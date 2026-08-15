import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def count_solutions(board, limit=2):
    """Count valid Sudoku completions up to a limit.

    The helper stops as soon as it finds the requested number of solutions so it
    can distinguish between zero, one, and multiple valid completions.
    """
    board = deep_copy(board)

    def backtrack():
        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] == EMPTY:
                    total = 0
                    for num in range(1, SIZE + 1):
                        if is_safe(board, row, col, num):
                            board[row][col] = num
                            total += backtrack()
                            if total >= limit:
                                board[row][col] = EMPTY
                                return total
                            board[row][col] = EMPTY
                    return total
        return 1

    return backtrack()


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board, clues):
    target_empty_cells = SIZE * SIZE - clues
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        if sum(cell == EMPTY for row_values in board for cell in row_values) >= target_empty_cells:
            break
        if board[row][col] == EMPTY:
            continue

        original_value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) != 1:
            board[row][col] = original_value

    return board


def generate_puzzle(clues=35):
    if not 1 <= clues <= SIZE * SIZE:
        raise ValueError(f'clues must be between 1 and {SIZE * SIZE}.')

    target_empty_cells = SIZE * SIZE - clues
    max_retries = 100

    for _ in range(max_retries):
        board = create_empty_board()
        if not fill_board(board):
            continue

        solution = deep_copy(board)
        puzzle = deep_copy(board)
        remove_cells(puzzle, clues)

        if sum(cell == EMPTY for row_values in puzzle for cell in row_values) == target_empty_cells:
            if count_solutions(puzzle, limit=2) == 1:
                return puzzle, solution

    raise RuntimeError(
        f'Unable to generate a unique puzzle with {clues} clues after {max_retries} attempts.'
    )
