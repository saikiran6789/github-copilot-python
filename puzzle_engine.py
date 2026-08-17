from copy import deepcopy

import sudoku_logic


class PuzzleEngine:
    """Coordinates Sudoku puzzle creation and answer checking."""

    def build_puzzle(self, target_clues=35):
        puzzle, solution = sudoku_logic.generate_puzzle(
            clues=target_clues
        )
        return deepcopy(puzzle), deepcopy(solution)

    @staticmethod
    def diff_against_solution(board, solution):
        differences = []

        for row_index in range(sudoku_logic.SIZE):
            for col_index in range(sudoku_logic.SIZE):
                value = board[row_index][col_index]

                # Empty cells are not treated as incorrect yet.
                if value == sudoku_logic.EMPTY:
                    continue

                if value != solution[row_index][col_index]:
                    differences.append((row_index, col_index))

        return differences

    @staticmethod
    def is_complete_and_correct(board, solution):
        if not isinstance(board, list):
            return False

        if len(board) != sudoku_logic.SIZE:
            return False

        for row_index in range(sudoku_logic.SIZE):
            if not isinstance(board[row_index], list):
                return False

            if len(board[row_index]) != sudoku_logic.SIZE:
                return False

            for col_index in range(sudoku_logic.SIZE):
                if board[row_index][col_index] != solution[row_index][col_index]:
                    return False

        return True