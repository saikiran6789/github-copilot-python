# Flask Sudoku Game

A browser-based Sudoku game built with Flask, vanilla JavaScript, and Python logic.

## Features

- Unique-solution Sudoku puzzle generation
- Easy, Medium, and Hard difficulty levels
- Immediate invalid-entry feedback
- Check Solution validation
- Completion message when the puzzle is solved
- Hint button that fills and locks one correct cell
- Game timer with reset and stop behavior
- Top 10 fastest times leaderboard stored in browser localStorage
- Dark and light theme toggle with persistence
- Alternating 3x3 box colors
- Responsive layout for desktop, tablet, and mobile
- Accessibility improvements for controls and readability

## Requirements

- Python 3
- Flask

## Setup

1. Open a terminal in the project folder.
2. Create and activate a virtual environment if desired.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the app

```bash
python app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://127.0.0.1:5000/
```

## Run tests

```bash
pytest
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
