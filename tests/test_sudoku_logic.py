import random

import pytest

import sudoku_logic


def count_valid_completions(grid, limit=2):
    """Count Sudoku solutions, stopping once the limit is reached."""
    working_grid = [row[:] for row in grid]

    def search():
        empty_cell = find_empty_cell(working_grid)

        if empty_cell is None:
            return 1

        row, col = empty_cell
        found = 0

        for value in range(1, sudoku_logic.SIZE + 1):
            if sudoku_logic.is_safe(working_grid, row, col, value):
                working_grid[row][col] = value
                found += search()
                working_grid[row][col] = sudoku_logic.EMPTY

                if found >= limit:
                    return found

        return found

    return search()


def find_empty_cell(grid):
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if grid[row][col] == sudoku_logic.EMPTY:
                return row, col

    return None


def number_of_clues(grid):
    return sum(
        value != sudoku_logic.EMPTY
        for row in grid
        for value in row
    )


def assert_valid_solution(solution):
    expected = list(range(1, sudoku_logic.SIZE + 1))

    for row in solution:
        assert sorted(row) == expected

    for col in range(sudoku_logic.SIZE):
        assert sorted(solution[row][col] for row in range(sudoku_logic.SIZE)) == expected

    for box_row in range(0, sudoku_logic.SIZE, 3):
        for box_col in range(0, sudoku_logic.SIZE, 3):
            values = [
                solution[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            ]
            assert sorted(values) == expected


def test_empty_board_shape():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(
        value == sudoku_logic.EMPTY
        for row in board
        for value in row
    )


def test_safety_rules():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 0, 1, 5) is False
    assert sudoku_logic.is_safe(board, 1, 0, 5) is False
    assert sudoku_logic.is_safe(board, 1, 1, 5) is False
    assert sudoku_logic.is_safe(board, 3, 3, 5) is True


@pytest.mark.parametrize("clues", [45, 35, 25])
def test_requested_difficulty_has_correct_clue_count(clues):
    random.seed(0)

    puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)

    assert number_of_clues(puzzle) == clues
    assert puzzle != solution
    assert count_valid_completions(puzzle) == 1


@pytest.mark.parametrize("clues", [45, 35, 25])
def test_multiple_puzzles_remain_unique(clues):
    for seed in range(5):
        random.seed(seed)

        puzzle, _ = sudoku_logic.generate_puzzle(clues=clues)

        assert count_valid_completions(puzzle, limit=2) == 1


def test_generated_solution_is_valid():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=30)

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)

    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in solution)

    assert_valid_solution(solution)

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            puzzle_value = puzzle[row][col]

            assert (
                puzzle_value == sudoku_logic.EMPTY
                or puzzle_value == solution[row][col]
            )