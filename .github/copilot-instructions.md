# Sudoku Game - GitHub Copilot Instructions

This is a browser-based Sudoku game built with Flask, vanilla JavaScript, and Python backtracking logic. The server keeps the solution private, and the UI validates and hints dynamically.

## Project Architecture

### Backend (Flask)
- **app.py**: Flask server with REST API endpoints for puzzle creation, validation, hints, and session management
- **puzzle_engine.py**: Orchestrates puzzle generation and solution comparison logic
- **sudoku_logic.py**: Core Sudoku algorithms—board generation, validation, solution counting, and clue removal

### Frontend (Vanilla JS + HTML/CSS)
- **templates/index.html**: Main page structure with board, controls, difficulty selector, scoreboard, and accessibility features
- **static/main.js**: Client-side rendering, UI interactions, timer, hint tracking, theme toggle, and localStorage score management
- **static/styles.css**: Responsive design with light/dark mode, alternating 3x3 box colors, and accessible styling

## Key Constraints

1. **Server-side Solution Storage**: The solution is never sent to the browser or exposed in localStorage/devtools. The session cookie only stores an opaque `game_id`; the actual puzzle and solution live in the `GAMES` dict on the server.

2. **Unique-Solution Guarantee**: Every generated puzzle has exactly one valid solution. The `count_solutions()` backtracking function (in sudoku_logic.py) counts valid completions up to a limit of 2, stopping early to avoid expensive full counts. Only clues removed during carving preserve uniqueness.

3. **Exact Clue Counts**:
   - Easy: 45 clues (36 empty cells)
   - Medium: 35 clues (46 empty cells)
   - Hard: 25 clues (56 empty cells)

4. **API Validation**: All endpoints validate input and return HTTP 400 for malformed requests (missing JSON, invalid board structure, unsupported clue counts, invalid cell values).

5. **Hints Tracking**: Hints are tracked on the server per game and included in the final score entry. Hinted cells are locked and visually distinguished.

## API Endpoints

### POST `/api/puzzles`
Create a new puzzle for the session.

**Request**:
```json
{"clues": 35}
```
or `?clues=35` query string (defaults to 35)

**Response** (201):
```json
{
  "game_id": "opaque-uuid-hex",
  "puzzle": [[0, 5, 0, ...], ...],
  "clues": 35
}
```

**Validation**:
- `clues` must be in {25, 35, 45} (Hard, Medium, Easy)
- Non-integer clues return HTTP 400
- Stores hints_used=0, difficulty name, puzzle, and solution server-side

### GET `/api/puzzles/current`
Fetch the current puzzle grid and game metadata.

**Response** (200):
```json
{
  "game_id": "...",
  "puzzle": [[...], ...],
  "hints_used": 2,
  "difficulty": "Medium"
}
```

### POST `/api/puzzles/current/check`
Check a submitted board against the solution.

**Request**:
```json
{"board": [[1, 2, 3, ...], ...]}
```

**Response** (200):
```json
{
  "incorrect_cells": [[0, 1], [2, 3]],
  "solved": false
}
```

**Validation**:
- Requires valid JSON body
- `board` must be present
- `board` must be a 9×9 list of lists
- Each cell must be an integer in [0, 9]
- Returns HTTP 400 with descriptive error message for any violation

### POST `/api/puzzles/current/hint`
Get a hint for the first empty cell.

**Response** (200):
```json
{
  "row": 0,
  "col": 5,
  "value": 7,
  "hints_used": 1
}
```

**Behavior**:
- Returns the row, column, and correct value for the first empty cell
- Increments hints_used on the server
- Returns HTTP 400 if no empty cells remain

### DELETE `/api/puzzles/current`
Abandon the current game and free server memory.

**Response** (204): No Content

## Frontend Features

1. **Difficulty Selection**: Dropdown to choose Easy/Medium/Hard; changing difficulty starts a new game.

2. **Timer**: Starts on new game, stops on completion, displays in MM:SS format.

3. **Hint Button**: Fills one empty cell with the correct value, locks it, and increments the hints counter. Displays "Hint used! (N total)".

4. **Check Solution**: Validates the board against the server solution, highlights incorrect cells, and shows completion message on success.

5. **Immediate Conflict Feedback**: As the player types, the board detects row/column/3×3 box duplicates and applies the "incorrect" class in real-time.

6. **Alternating 3×3 Colors**: Each of the nine 3×3 regions alternates between two semi-transparent colors for visual distinction.

7. **Dark/Light Mode**: Toggle button persists the selected theme in localStorage. Respects system preference if no saved theme.

8. **Top 10 Scoreboard**: Displays the fastest completion times, sorted by elapsed time. Records name, time, difficulty, and hints used. Stored in localStorage with safety checks for corrupted data.

9. **Responsive Design**: Board fits ~360px mobile screens without horizontal scrolling. Controls flex/wrap appropriately.

10. **Accessibility**: Aria labels for all controls, aria-live regions for messages and timer, semantic HTML (table with `<thead>` and `scope` attributes).

## Testing

### Unit Tests (tests/test_sudoku_logic.py)
- Verify `is_safe()` correctly rejects duplicates
- Ensure generated puzzles have exactly one solution
- Confirm exact clue counts for all three difficulties
- Validate solution structure (rows, columns, boxes are permutations of 1-9)

### Integration Tests (tests/test_app.py)
- Verify the `/` route returns HTML
- Test puzzle creation with various clue counts
- Confirm solution is never exposed in responses
- Verify current puzzle retrieval
- Check incorrect cell reporting and solved state
- Test session abandonment

### Running Tests
```bash
pytest -q
```

Pytest is configured in `pytest.ini` to collect tests from the `tests/` folder.

## Development Workflow

1. **Start the Server**:
   ```bash
   python app.py
   ```
   Flask runs on `http://127.0.0.1:5000/` by default.

2. **Create a Puzzle**:
   - Browser loads index.html, which calls `newGame()` on load
   - newGame() POSTs to `/api/puzzles` with default difficulty
   - Frontend renders the puzzle grid and starts the timer

3. **Add a Hint**:
   - Player clicks Hint button
   - Frontend POSTs to `/api/puzzles/current/hint`
   - Server finds the first empty cell and increments hints_used
   - Frontend fills the cell, locks it, and displays "Hint used! (N total)"

4. **Complete the Puzzle**:
   - Player fills all cells
   - Clicks Check Solution
   - Frontend POSTs board to `/api/puzzles/current/check`
   - Server compares against solution
   - If solved, frontend shows congratulations message
   - Prompts for name and stores the score with time, difficulty, and hints_used

## Common Modifications

### Add a New Difficulty Level
1. Update `DIFFICULTY_TO_CLUES` in main.js
2. Add `<option>` to `#difficulty-select` in index.html
3. Update `VALID_CLUES` in app.py
4. Update `CLUES_TO_DIFFICULTY` in app.py
5. Add test case in test_app.py

### Adjust Puzzle Generation Retry Limit
- Edit `max_retries` in `sudoku_logic.generate_puzzle()`
- Default is 100; higher values increase generation time but rarely needed

### Change Theme Colors
- Edit CSS variables in `:root` and `body[data-theme="dark"]` in styles.css
- All component colors reference these variables for consistent theming

### Modify Board Size
- This is not recommended; Sudoku is 9×9. To change:
  - Update `SIZE = 9` in both sudoku_logic.py and main.js
  - Adjust CSS grid and responsive breakpoints in styles.css
  - Update all validation and test expectations

## Debugging

- **Board rendering issues**: Check browser devtools Network tab to confirm `/api/puzzles` returns a valid puzzle
- **Hint not appearing**: Verify the cell index calculation: `index = row * SIZE + col`
- **Scores not persisting**: Check browser localStorage quota and browser devtools Console for storage errors
- **Solution exposure**: Never return the `solution` field in API responses; check response JSONs in devtools Network tab
- **Puzzle not unique**: Run `pytest tests/test_sudoku_logic.py::test_generate_puzzle_has_exactly_one_solution -v` to verify the generation algorithm

## Performance Notes

- Puzzle generation typically takes 200–500 ms per puzzle (depends on difficulty and random seed)
- Solution counting (via `count_solutions()`) is limited to 2 completions to avoid expensive exhaustive search
- The server stores active games in memory; without cleanup, `GAMES` grows unbounded. Use DELETE `/api/puzzles/current` or a periodic cleanup task in production

## Deployment Considerations

- Set `SUDOKU_SECRET_KEY` environment variable for production (default is "dev-secret-change-me")
- Run Flask with a production WSGI server (e.g., Gunicorn) instead of the development server
- Consider a session store (e.g., Redis or database) if scaling to multiple Flask instances
- Monitor `GAMES` dictionary size and implement active game timeout cleanup
- Use HTTPS in production to protect session cookies
