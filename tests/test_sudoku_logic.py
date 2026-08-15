import random

import pytest

import sudoku_logic


def count_solutions(board, limit=2):
    """Test-only helper: count valid Sudoku completions up to a limit.

    This is intentionally kept in the test suite so the production application
    logic remains untouched while we check whether a puzzle has a unique answer.
    """
    board = [row[:] for row in board]

    def backtrack():
        for row in range(sudoku_logic.SIZE):
            for col in range(sudoku_logic.SIZE):
                if board[row][col] == sudoku_logic.EMPTY:
                    total = 0
                    for num in range(1, sudoku_logic.SIZE + 1):
                        if sudoku_logic.is_safe(board, row, col, num):
                            board[row][col] = num
                            total += backtrack()
                            if total >= limit:
                                board[row][col] = sudoku_logic.EMPTY
                                return total
                            board[row][col] = sudoku_logic.EMPTY
                    return total
        return 1

    return backtrack()


def test_create_empty_board_has_9_by_9_zero_grid():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_rejects_duplicates_in_row_column_and_box():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    assert not sudoku_logic.is_safe(board, 1, 0, 5)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)
    assert sudoku_logic.is_safe(board, 3, 3, 5)


def test_generate_puzzle_has_exactly_one_solution():
    for seed in range(10):
        random.seed(seed)
        puzzle, _ = sudoku_logic.generate_puzzle(clues=30)

        solution_count = count_solutions(puzzle, limit=2)
        assert solution_count == 1


@pytest.mark.parametrize('clues', [45, 35, 25])
def test_generate_puzzle_uses_exact_requested_clue_count(clues):
    random.seed(0)
    puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert sum(cell == 0 for row in puzzle for cell in row) == (81 - clues)
    assert sum(value != 0 for row in puzzle for value in row) == clues
    assert count_solutions(puzzle, limit=2) == 1
    assert puzzle != solution


def test_generate_puzzle_returns_valid_solution_and_puzzle():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=30)

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert all(0 <= value <= 9 for row in puzzle for value in row)
    assert all(1 <= value <= 9 for row in solution for value in row)
    assert sum(cell == 0 for row in puzzle for cell in row) == 81 - 30

    for row in solution:
        assert sorted(row) == list(range(1, 10))

    for col in range(sudoku_logic.SIZE):
        assert sorted(row[col] for row in solution) == list(range(1, 10))

    for row_start in range(0, sudoku_logic.SIZE, 3):
        for col_start in range(0, sudoku_logic.SIZE, 3):
            values = []
            for row in range(row_start, row_start + 3):
                for col in range(col_start, col_start + 3):
                    values.append(solution[row][col])
            assert sorted(values) == list(range(1, 10))

    for row_index, row in enumerate(puzzle):
        for col_index, value in enumerate(row):
            assert value == 0 or value == solution[row_index][col_index]
