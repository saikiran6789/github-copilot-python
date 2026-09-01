import copy
import random

SIZE = 9
BOX_SIZE = 3
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY] * SIZE for _ in range(SIZE)]


def row_values(board, row):
    return set(board[row])


def column_values(board, col):
    return {board[row][col] for row in range(SIZE)}


def box_values(board, row, col):
    top = (row // BOX_SIZE) * BOX_SIZE
    left = (col // BOX_SIZE) * BOX_SIZE

    return {
        board[r][c]
        for r in range(top, top + BOX_SIZE)
        for c in range(left, left + BOX_SIZE)
    }


def available_numbers(board, row, col):
    used = (
        row_values(board, row)
        | column_values(board, col)
        | box_values(board, row, col)
    )

    return [
        value
        for value in range(1, SIZE + 1)
        if value not in used
    ]


def is_safe(board, row, col, num):
    if board[row][col] not in (EMPTY, num):
        return False

    return num in available_numbers(board, row, col)


def find_empty_cell(board):
    """Return the empty cell with the fewest possible values."""
    best_cell = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue

            candidates = available_numbers(board, row, col)

            if not candidates:
                return row, col, []

            if best_candidates is None or len(candidates) < len(best_candidates):
                best_cell = (row, col)
                best_candidates = candidates

                if len(candidates) == 1:
                    return row, col, candidates

    if best_cell is None:
        return None

    return best_cell[0], best_cell[1], best_candidates


def fill_board(board):
    cell = find_empty_cell(board)

    if cell is None:
        return True

    row, col, candidates = cell

    random.shuffle(candidates)

    for value in candidates:
        board[row][col] = value

        if fill_board(board):
            return True

        board[row][col] = EMPTY

    return False


def count_solutions(board, limit=2):
    working = deep_copy(board)
    found = 0

    def search():
        nonlocal found

        if found >= limit:
            return

        cell = find_empty_cell(working)

        if cell is None:
            found += 1
            return

        row, col, candidates = cell

        for value in candidates:
            working[row][col] = value
            search()
            working[row][col] = EMPTY

            if found >= limit:
                return

    search()
    return found


def remove_cells(board, clues):
    target_empty = SIZE * SIZE - clues

    positions = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
    ]
    random.shuffle(positions)

    removed = 0

    for row, col in positions:
        if removed >= target_empty:
            break

        previous = board[row][col]

        if previous == EMPTY:
            continue

        board[row][col] = EMPTY

        if count_solutions(board, limit=2) == 1:
            removed += 1
        else:
            board[row][col] = previous

    return board


def generate_puzzle(clues=35):
    if not 1 <= clues <= SIZE * SIZE:
        raise ValueError(
            f"clues must be between 1 and {SIZE * SIZE}."
        )

    required_empty = SIZE * SIZE - clues

    for _ in range(100):
        completed = create_empty_board()

        if not fill_board(completed):
            continue

        solution = deep_copy(completed)
        puzzle = deep_copy(completed)

        remove_cells(puzzle, clues)

        empty_count = sum(
            value == EMPTY
            for row in puzzle
            for value in row
        )

        if empty_count == required_empty and count_solutions(puzzle, 2) == 1:
            return puzzle, solution

    raise RuntimeError(
        f"Unable to generate a unique puzzle with {clues} clues."
    )