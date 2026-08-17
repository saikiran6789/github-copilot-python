# Flask Sudoku Game

A browser-based Sudoku game built with Flask, vanilla JavaScript, and Python backtracking logic. The server keeps the solution private, and the UI validates and hints dynamically.

## Features

- **Unique-solution Sudoku puzzle generation** with exactly one valid solution guaranteed
- **Easy, Medium, and Hard difficulty levels** (45, 35, and 25 clues respectively)
- **Immediate invalid-entry feedback** - detects row/column/3×3 box conflicts as you type
- **Check Solution validation** - highlights incorrect cells
- **Completion message** when the puzzle is solved successfully
- **Hint button** that fills and locks one correct cell, with hint counter
- **Game timer** that starts on new game and stops after completion
- **Top 10 fastest times leaderboard** stored in browser localStorage with name, time, difficulty, and hints used
- **Dark and light theme toggle** with localStorage persistence and system preference detection
- **Alternating 3×3 box colors** for better visual distinction
- **Responsive layout** for desktop, tablet, and mobile (fits ~360px screens)
- **Accessibility** with aria labels, aria-live regions, and semantic HTML
- **Server-side solution storage** - solution never exposed to browser or devtools

## Project Structure

```
.
├── app.py                   # Flask server with API endpoints
├── puzzle_engine.py         # Puzzle generation orchestration
├── sudoku_logic.py          # Core Sudoku algorithms (generation, validation, solution counting)
├── requirements.txt         # Python dependencies
├── pytest.ini               # Pytest configuration
├── README.md                # This file
├── .github/
│   └── copilot-instructions.md  # Repository-specific Copilot instructions
├── templates/
│   └── index.html           # Main HTML page
├── static/
│   ├── main.js              # Client-side logic and interactions
│   └── styles.css           # Styling with light/dark mode and responsive design
└── tests/
    ├── test_app.py          # Integration tests for Flask API
    └── test_sudoku_logic.py  # Unit tests for Sudoku algorithms
```

## Requirements

- Python 3.8+
- Flask 2.0+
- pytest 8.0+ (for testing)

## Setup

1. **Clone or download the repository** and navigate to the project directory.

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python app.py
```

The Flask development server will start on `http://127.0.0.1:5000/`. Open this URL in your browser to play the game.

### Development Mode

The server runs in debug mode by default, which enables:
- Auto-reloading when you modify Python files
- Detailed error pages with stack traces
- Built-in debugger

### Production Deployment

For production, use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn app:app
```

## Running Tests

Run all tests with pytest:
```bash
pytest -q
```

For verbose output:
```bash
pytest -v
```

Run only Sudoku logic tests:
```bash
pytest tests/test_sudoku_logic.py -v
```

Run only API tests:
```bash
pytest tests/test_app.py -v
```

Run a specific test:
```bash
pytest tests/test_sudoku_logic.py::test_generate_puzzle_has_exactly_one_solution -v
```

## How the Unique-Solution Algorithm Works

Every generated puzzle is guaranteed to have exactly one valid solution through the following process:

1. **Generate a complete solution**: Fill the entire 9×9 board with valid Sudoku digits using backtracking.

2. **Carve cells**: Start with the complete solution and randomly remove clues one by one.

3. **Verify uniqueness**: Before permanently removing each clue, test the puzzle with `count_solutions()`. This function counts valid completions up to a limit of 2, stopping early once it finds 2+ solutions.

4. **Only keep valid removals**: Only keep the removed clue if the puzzle still has exactly one solution.

5. **Reach target clue count**: Continue until the puzzle has the requested number of clues (25, 35, or 45).

The `count_solutions()` function is crucial for performance—it limits the search to a small count rather than exhaustively finding all solutions, making generation feasible even for hard puzzles.

## API Endpoints

See [.github/copilot-instructions.md](.github/copilot-instructions.md) for comprehensive API documentation, including request/response formats, validation rules, and error handling.

### Quick Reference

- **POST `/api/puzzles`** - Create a new puzzle
  - Query: `?clues=35` or JSON body: `{"clues": 35}`
  - Valid clues: 25, 35, 45
  - Returns 201 with puzzle and game_id

- **GET `/api/puzzles/current`** - Get current puzzle and metadata
  - Returns 200 with puzzle, hints_used, difficulty

- **POST `/api/puzzles/current/check`** - Check submitted board
  - JSON body: `{"board": [[...], [...], ...]}`
  - Returns 200 with incorrect_cells and solved flag

- **POST `/api/puzzles/current/hint`** - Get a hint
  - Returns 200 with row, col, value, and hints_used counter

- **DELETE `/api/puzzles/current`** - Abandon current game
  - Returns 204 (No Content)

## Configuration

### Environment Variables

- `SUDOKU_SECRET_KEY`: Flask session secret key (default: "dev-secret-change-me")
  - **Important**: Set this to a random value in production

### Browser Storage

- **Theme**: Persisted in localStorage as `sudoku-theme-v1` (values: "light" or "dark")
- **Scores**: Persisted in localStorage as `sudoku-top-scores-v1` (JSON array of score records)

## Troubleshooting

**Board rendering issues**: Check browser DevTools Network tab to confirm `/api/puzzles` returns a valid puzzle.

**Hint not appearing**: Verify cell index calculation in browser console.

**Scores not persisting**: Check browser DevTools Application tab → Storage → LocalStorage. Ensure localStorage quota is not exceeded.

**Solution exposure**: Search for "solution" in Network tab responses—it should never appear.

**Puzzle not unique**: Run `pytest tests/test_sudoku_logic.py::test_generate_puzzle_has_exactly_one_solution -v` to verify the generation algorithm.

## Performance Notes

- **Puzzle generation**: Typically takes 200–500 ms per puzzle (varies by difficulty and random seed)
- **Solution counting**: Limited to 2 completions to avoid expensive exhaustive search
- **Server memory**: Active games stored in `GAMES` dict. Use DELETE endpoint or implement cleanup in production

## License

This project is provided as-is for educational purposes.
```

## Project structure

- `app.py` - Flask routes and active puzzle state
- `sudoku_logic.py` - Sudoku generation and validation logic
- `static/` - JavaScript and CSS files
- `templates/` - HTML templates
- `tests/` - Automated tests
- `Screenshots/` - Evidence images for milestones and final verification

## Notes

- The Sudoku generation logic remains unchanged from the puzzle requirements and produces a unique-solution board.
- The timer and scoreboard are browser-side only and persist in localStorage.
- The game is intentionally kept simple and does not include Dark Mode, responsive styling, alternating 3x3 colors, note mode, or solver features beyond the required implementation.
