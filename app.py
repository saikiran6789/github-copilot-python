
import os
import uuid
import sudoku_logic
from flask import Flask, render_template, jsonify, request, session

from puzzle_engine import PuzzleEngine

app = Flask(__name__)
app.secret_key = os.environ.get("SUDOKU_SECRET_KEY", "dev-secret-change-me")

# Server-side table of active games, keyed by an opaque game_id.
# The session cookie only stores the id, never the solution itself, so
# the solution is never exposed to the browser/devtools.
GAMES = {}

# Map clue counts to difficulty names
CLUES_TO_DIFFICULTY = {
    45: "Easy",
    35: "Medium",
    25: "Hard",
}


def _get_difficulty_name(clues):
    """Get the human-readable difficulty name for a clue count."""
    return CLUES_TO_DIFFICULTY.get(clues, "Unknown")


def _get_active_game():
    """Looks up the game belonging to the current browser session.
    Returns (None, None) if this visitor has no puzzle in progress."""
    game_id = session.get("game_id")
    if not game_id:
        return None, None
    return game_id, GAMES.get(game_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/puzzles", methods=["POST"])
def create_puzzle():
    """Creates a new puzzle for this browser session.
    Accepts clue count either as JSON body {"clues": N} or a query
    string ?clues=N, defaulting to 35 if neither is given.
    
    Validates that clues is one of: 25, 35, 45 (Easy, Medium, Hard).
    Returns HTTP 400 with a JSON error if invalid.
    """
    VALID_CLUES = {25, 35, 45}
    
    payload = request.get_json(silent=True) or {}
    clue_count_str = payload.get("clues", request.args.get("clues", None))
    
    # Default to 35 if not specified
    if clue_count_str is None:
        clue_count = 35
    else:
        # Validate that it's a valid clue count
        try:
            clue_count = int(clue_count_str)
        except (ValueError, TypeError):
            return jsonify({
                "error": "clues must be an integer"
            }), 400
    
    if clue_count not in VALID_CLUES:
        return jsonify({
            "error": f"clues must be one of {sorted(VALID_CLUES)}"
        }), 400

    # Build a fresh solved grid + puzzle carved from it.
    engine = PuzzleEngine()
    puzzle, solution = engine.build_puzzle(target_clues=clue_count)

    # Store both grids server-side under a random id; only the id goes
    # into the session cookie, so the client never sees the solution.
    game_id = uuid.uuid4().hex
    GAMES[game_id] = {
        "puzzle": puzzle,
        "solution": solution,
        "hints_used": 0,
        "difficulty": _get_difficulty_name(clue_count),
    }
    session["game_id"] = game_id

    return jsonify({
        "game_id": game_id,
        "puzzle": puzzle,   # solution intentionally omitted from the response
        "clues": clue_count,
    }), 201  # 201 Created, since this endpoint creates a new resource


@app.route("/api/puzzles/current", methods=["GET"])
def get_current_puzzle():
    """Returns the puzzle grid (not the solution) for the active session.
    Lets the frontend re-fetch the board on page reload without the
    server needing to push state proactively."""
    game_id, game = _get_active_game()
    if game is None:
        return jsonify({"error": "no active puzzle for this session"}), 404
    return jsonify({
        "game_id": game_id,
        "puzzle": game["puzzle"],
        "hints_used": game.get("hints_used", 0),
        "difficulty": game.get("difficulty", "Unknown"),
    })


@app.route("/api/puzzles/current/check", methods=["POST"])
def check_current_puzzle():
    """Validates a submitted board against the session's stored solution.
    Modeled as an action on the puzzle sub-resource (POST .../check)
    rather than a standalone /check verb endpoint.
    
    Returns HTTP 400 if the JSON is missing, malformed, or board is invalid.
    """
    _, game = _get_active_game()
    if game is None:
        return jsonify({"error": "no active puzzle for this session"}), 404

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "request body must be valid JSON"}), 400
    
    submitted_board = payload.get("board")
    if submitted_board is None:
        return jsonify({"error": "request body must include 'board'"}), 400
    
    # Validate board structure
    if not isinstance(submitted_board, list):
        return jsonify({"error": "board must be a list"}), 400
    
    if len(submitted_board) != 9:
        return jsonify({"error": "board must have 9 rows"}), 400
    
    for row_idx, row in enumerate(submitted_board):
        if not isinstance(row, list):
            return jsonify({"error": f"row {row_idx} must be a list"}), 400
        if len(row) != 9:
            return jsonify({"error": f"row {row_idx} must have 9 columns"}), 400
        for col_idx, cell in enumerate(row):
            if not isinstance(cell, int):
                return jsonify({
                    "error": f"cell [{row_idx}][{col_idx}] must be an integer"
                }), 400
            if not (0 <= cell <= 9):
                return jsonify({
                    "error": f"cell [{row_idx}][{col_idx}] must be between 0 and 9"
                }), 400

    solution = game["solution"]

    # Find every cell that's filled in but wrong (blanks are ignored).
    mismatches = PuzzleEngine.diff_against_solution(submitted_board, solution)

    # "Solved" means no mismatches AND every cell is actually filled in —
    # an all-blank board would have zero mismatches but isn't solved.
    solved = not mismatches and PuzzleEngine.is_complete_and_correct(submitted_board, solution)

    return jsonify({
        "incorrect_cells": [[r, c] for r, c in mismatches],
        "solved": solved,
    })


@app.route("/api/puzzles/current", methods=["DELETE"])
def abandon_puzzle():
    """Ends the active session's game and frees its server-side memory.
    Without this, GAMES would grow forever as visitors start new puzzles."""
    game_id = session.pop("game_id", None)
    if game_id:
        GAMES.pop(game_id, None)
    return "", 204  # 204 No Content: successful, nothing to return


@app.route("/api/puzzles/current/hint", methods=["POST"])
def get_hint():
    """Return one correct value for an empty cell without exposing the solution.
    Increments the hints-used counter on the server.
    """
    game_id, game = _get_active_game()

    if game is None:
        return jsonify({
            "error": "no active puzzle for this session"
        }), 404

    puzzle = game["puzzle"]
    solution = game["solution"]

    # Find the first empty cell
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] == 0:
                # Increment hints used on the server
                game["hints_used"] = game.get("hints_used", 0) + 1
                
                return jsonify({
                    "row": row,
                    "col": col,
                    "value": solution[row][col],
                    "hints_used": game["hints_used"],
                })

    return jsonify({
        "error": "no empty cells remain"
    }), 400




if __name__ == "__main__":
    app.run(debug=True)
    
