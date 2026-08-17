// Client-side rendering and interaction for the Flask-backed Sudoku

const SIZE = 9;

const DIFFICULTY_TO_CLUES = {
  easy: 45,
  medium: 35,
  hard: 25
};

const SCOREBOARD_STORAGE_KEY = 'sudoku-top-scores-v1';
const THEME_STORAGE_KEY = 'sudoku-theme-v1';

let puzzle = [];
let currentSolution = [];
let elapsedSeconds = 0;
let timerInterval = null;
let gameStartedAt = 0;
let gameSolved = false;
let scoreSavedForCurrentGame = false;
let hintsUsed = 0;


// --------------------------------------------------
// Difficulty
// --------------------------------------------------

function updateDifficultyDisplay() {
  const select = document.getElementById('difficulty-select');
  const display = document.getElementById('current-difficulty');

  if (!select || !display) {
    return;
  }

  const label =
    select.value.charAt(0).toUpperCase() + select.value.slice(1);

  display.innerText = `Current difficulty: ${label}`;
}


function getSelectedClues() {
  const select = document.getElementById('difficulty-select');

  if (!select) {
    return DIFFICULTY_TO_CLUES.medium;
  }

  return DIFFICULTY_TO_CLUES[select.value] ||
         DIFFICULTY_TO_CLUES.medium;
}


// --------------------------------------------------
// Timer
// --------------------------------------------------

function updateTimerDisplay() {
  const timerEl = document.getElementById('timer');

  if (!timerEl) {
    return;
  }

  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;

  timerEl.innerText =
    `Time: ${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}


function clearTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}


function startTimer() {
  clearTimer();

  elapsedSeconds = 0;
  gameStartedAt = Date.now();

  updateTimerDisplay();

  timerInterval = setInterval(() => {
    if (!gameSolved) {
      elapsedSeconds =
        Math.floor((Date.now() - gameStartedAt) / 1000);

      updateTimerDisplay();
    }
  }, 1000);
}


// --------------------------------------------------
// Theme
// --------------------------------------------------

function applyTheme(theme) {
  const normalizedTheme =
    theme === 'dark' ? 'dark' : 'light';

  document.body.dataset.theme = normalizedTheme;

  const toggleButton =
    document.getElementById('theme-toggle');

  if (toggleButton) {
    const isDark = normalizedTheme === 'dark';

    toggleButton.textContent =
      isDark ? 'Light Mode' : 'Dark Mode';

    toggleButton.setAttribute(
      'aria-pressed',
      String(isDark)
    );

    toggleButton.setAttribute(
      'aria-label',
      isDark
        ? 'Switch to light mode'
        : 'Switch to dark mode'
    );
  }

  try {
    localStorage.setItem(
      THEME_STORAGE_KEY,
      normalizedTheme
    );
  } catch (error) {
    // Ignore storage errors.
  }
}


function initializeTheme() {
  try {
    const storedTheme =
      localStorage.getItem(THEME_STORAGE_KEY);

    const prefersDark =
      window.matchMedia &&
      window.matchMedia(
        '(prefers-color-scheme: dark)'
      ).matches;

    const defaultTheme =
      storedTheme ||
      (prefersDark ? 'dark' : 'light');

    applyTheme(defaultTheme);

  } catch (error) {
    applyTheme('light');
  }
}


// --------------------------------------------------
// Sudoku validation
// --------------------------------------------------

function hasConflict(board, row, col, value) {
  if (!value) {
    return false;
  }

  // Check row
  for (let i = 0; i < SIZE; i++) {
    if (
      i !== col &&
      board[row][i] === value
    ) {
      return true;
    }
  }

  // Check column
  for (let i = 0; i < SIZE; i++) {
    if (
      i !== row &&
      board[i][col] === value
    ) {
      return true;
    }
  }

  // Check 3x3 box
  const startRow =
    Math.floor(row / 3) * 3;

  const startCol =
    Math.floor(col / 3) * 3;

  for (
    let i = startRow;
    i < startRow + 3;
    i++
  ) {
    for (
      let j = startCol;
      j < startCol + 3;
      j++
    ) {
      if (
        (i !== row || j !== col) &&
        board[i][j] === value
      ) {
        return true;
      }
    }
  }

  return false;
}


function applyImmediateValidation() {
  const boardDiv =
    document.getElementById('sudoku-board');

  if (!boardDiv) {
    return;
  }

  const inputs =
    boardDiv.getElementsByTagName('input');

  const board =
    Array.from(
      { length: SIZE },
      () => Array(SIZE).fill(0)
    );

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {

      const idx = i * SIZE + j;
      const input = inputs[idx];

      const rawValue =
        input.value.trim();

      if (rawValue !== '') {
        board[i][j] =
          parseInt(rawValue, 10);
      }
    }
  }

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {

      const idx = i * SIZE + j;
      const input = inputs[idx];

      if (input.disabled) {
        input.className =
          input.dataset.hinted === 'true'
            ? 'sudoku-cell hinted'
            : 'sudoku-cell prefilled';

        continue;
      }

      const rawValue =
        input.value.trim();

      const value =
        rawValue === ''
          ? 0
          : parseInt(rawValue, 10);

      input.className = 'sudoku-cell';

      if (
        value !== 0 &&
        hasConflict(board, i, j, value)
      ) {
        input.className =
          'sudoku-cell incorrect';
      }
    }
  }
}


// --------------------------------------------------
// Board
// --------------------------------------------------

function createBoardElement() {
  const boardDiv =
    document.getElementById('sudoku-board');

  if (!boardDiv) {
    return;
  }

  boardDiv.innerHTML = '';

  for (let i = 0; i < SIZE; i++) {

    const rowDiv =
      document.createElement('div');

    rowDiv.className = 'sudoku-row';

    for (let j = 0; j < SIZE; j++) {

      const input =
        document.createElement('input');

      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';

      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.hinted = 'false';

      input.setAttribute(
        'aria-label',
        `Row ${i + 1}, column ${j + 1}`
      );

      const boxRow =
        Math.floor(i / 3);

      const boxCol =
        Math.floor(j / 3);

      const boxVariant =
        (boxRow + boxCol) % 2 === 0
          ? 'var(--cell-box-a)'
          : 'var(--cell-box-b)';

      input.style.setProperty(
        '--cell-box-bg',
        boxVariant
      );

      input.addEventListener(
        'input',
        (event) => {

          const val =
            event.target.value
              .replace(/[^1-9]/g, '');

          event.target.value = val;

          applyImmediateValidation();
        }
      );

      rowDiv.appendChild(input);
    }

    boardDiv.appendChild(rowDiv);
  }
}


function renderPuzzle(puz) {
  puzzle = puz;

  createBoardElement();

  const boardDiv =
    document.getElementById('sudoku-board');

  const inputs =
    boardDiv.getElementsByTagName('input');

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {

      const idx = i * SIZE + j;
      const val = puzzle[i][j];

      const input = inputs[idx];

      input.dataset.hinted = 'false';

      if (val !== 0) {

        input.value = val;
        input.disabled = true;
        input.className =
          'sudoku-cell prefilled';

      } else {

        input.value = '';
        input.disabled = false;
        input.className =
          'sudoku-cell';
      }
    }
  }
}


// --------------------------------------------------
// Scoreboard
// --------------------------------------------------

function getStoredScores() {
  try {

    const rawScores =
      localStorage.getItem(
        SCOREBOARD_STORAGE_KEY
      );

    if (!rawScores) {
      return [];
    }

    const parsed =
      JSON.parse(rawScores);

    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .filter((entry) => {
        return (
          entry &&
          typeof entry.name === 'string' &&
          typeof entry.difficulty === 'string' &&
          Number.isFinite(entry.timeSeconds)
        );
      })
      .map((entry) => ({
        name:
          entry.name.trim() || 'Player',

        difficulty:
          entry.difficulty,

        timeSeconds:
          Number(entry.timeSeconds),
        
        hintsUsed:
          Number.isFinite(entry.hintsUsed) ? entry.hintsUsed : 0
      }));

  } catch (error) {
    return [];
  }
}


function persistScores(scores) {
  try {

    localStorage.setItem(
      SCOREBOARD_STORAGE_KEY,
      JSON.stringify(scores)
    );

  } catch (error) {
    // Ignore storage errors.
  }
}


function renderScoreboard() {
  const scores =
    getStoredScores()
      .sort(
        (a, b) =>
          a.timeSeconds - b.timeSeconds
      )
      .slice(0, 10);

  const tableBody =
    document.getElementById(
      'scoreboard-body'
    );

  const emptyMessage =
    document.getElementById(
      'scoreboard-empty'
    );

  const table =
    document.querySelector(
      '.scoreboard-table'
    );

  if (!tableBody || !emptyMessage || !table) {
    return;
  }

  tableBody.innerHTML = '';

  if (scores.length === 0) {

    table.hidden = true;
    emptyMessage.hidden = false;

    return;
  }

  table.hidden = false;
  emptyMessage.hidden = true;

  scores.forEach((score, index) => {

    const row =
      document.createElement('tr');

    const minutes =
      Math.floor(
        score.timeSeconds / 60
      );

    const seconds =
      score.timeSeconds % 60;

    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${score.name}</td>
      <td>${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}</td>
      <td>${score.difficulty}</td>
      <td>${score.hintsUsed || 0}</td>
    `;

    tableBody.appendChild(row);
  });
}


function recordSolvedGame() {

  if (scoreSavedForCurrentGame) {
    return;
  }

  const entryName =
    window.prompt(
      'You solved it! Enter your name for the leaderboard:',
      'Player'
    );

  const safeName =
    (
      entryName &&
      entryName.trim()
    )
      ? entryName.trim().slice(0, 30)
      : 'Player';

  const scores =
    getStoredScores();

  scores.push({
    name: safeName,

    difficulty:
      document.getElementById(
        'difficulty-select'
      ).value,

    timeSeconds:
      elapsedSeconds,
    
    hintsUsed:
      hintsUsed
  });

  scores.sort(
    (a, b) =>
      a.timeSeconds - b.timeSeconds
  );

  const topTen =
    scores.slice(0, 10);

  persistScores(topTen);
  renderScoreboard();

  scoreSavedForCurrentGame = true;
}


// --------------------------------------------------
// Hint
// --------------------------------------------------

function findHintCell() {

  const boardDiv =
    document.getElementById(
      'sudoku-board'
    );

  const inputs =
    boardDiv.getElementsByTagName('input');

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {

      const idx =
        i * SIZE + j;

      const input =
        inputs[idx];

      if (
        !input.disabled &&
        input.value === ''
      ) {
        return {
          row: i,
          col: j,
          input
        };
      }
    }
  }

  return null;
}


async function applyHint() {

  if (gameSolved) {
    const msg = document.getElementById('message');

    msg.style.color = '#d32f2f';
    msg.innerText = 'This game is already solved.';

    return;
  }

  const msg =
    document.getElementById('message');

  try {

    const response =
      await fetch(
        '/api/puzzles/current/hint',
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          }
        }
      );

    const data =
      await response.json();

    if (!response.ok) {

      msg.style.color = '#d32f2f';

      msg.innerText =
        data.error ||
        'Unable to get a hint.';

      return;
    }

    // Update hints used counter from server response
    if (Number.isFinite(data.hints_used)) {
      hintsUsed = data.hints_used;
    }

    const boardDiv =
      document.getElementById(
        'sudoku-board'
      );

    const inputs =
      boardDiv.getElementsByTagName('input');

    const index =
      data.row * SIZE + data.col;

    const input =
      inputs[index];

    if (!input) {

      msg.style.color = '#d32f2f';

      msg.innerText =
        'Unable to locate the hint cell.';

      return;
    }

    input.value = data.value;
    input.disabled = true;
    input.dataset.hinted = 'true';

    input.className =
      'sudoku-cell hinted';

    msg.style.color = '#1f7a1f';

    msg.innerText =
      `Hint used! (${hintsUsed} total)`;

  } catch (error) {

    console.error(
      'Hint error:',
      error
    );

    msg.style.color = '#d32f2f';

    msg.innerText =
      'Unable to get a hint. Check the Flask server.';
  }
}


// --------------------------------------------------
// NEW GAME
// --------------------------------------------------

async function newGame() {

  clearTimer();

  gameSolved = false;
  scoreSavedForCurrentGame = false;
  hintsUsed = 0;

  const clues =
    getSelectedClues();

  try {

    const response =
      await fetch(
        '/api/puzzles',
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          body: JSON.stringify({
            clues: clues
          })
        }
      );

    if (!response.ok) {

      throw new Error(
        `Server returned ${response.status}`
      );
    }

    const data =
      await response.json();

    renderPuzzle(data.puzzle);

    // Solution stays on the server.
    currentSolution = [];

    document.getElementById(
      'message'
    ).innerText = '';

    updateDifficultyDisplay();

    startTimer();

  } catch (error) {

    console.error(
      'Unable to start new game:',
      error
    );

    const msg =
      document.getElementById(
        'message'
      );

    msg.style.color = '#d32f2f';

    msg.innerText =
      'Could not load a new puzzle. Check the Flask server.';
  }
}


// --------------------------------------------------
// CHECK SOLUTION
// --------------------------------------------------

async function checkSolution() {

  const boardDiv =
    document.getElementById(
      'sudoku-board'
    );

  const inputs =
    boardDiv.getElementsByTagName('input');

  const board = [];

  for (let i = 0; i < SIZE; i++) {

    board[i] = [];

    for (let j = 0; j < SIZE; j++) {

      const idx =
        i * SIZE + j;

      const value =
        inputs[idx].value;

      board[i][j] =
        value
          ? parseInt(value, 10)
          : 0;
    }
  }

  try {

    const response =
      await fetch(
        '/api/puzzles/current/check',
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          body: JSON.stringify({
            board: board
          })
        }
      );

    const data =
      await response.json();

    const msg =
      document.getElementById(
        'message'
      );

    if (!response.ok || data.error) {

      msg.style.color = '#d32f2f';

      msg.innerText =
        data.error ||
        'Unable to check the puzzle.';

      return;
    }

    const incorrect =
      new Set(
        (data.incorrect_cells || [])
          .map(
            x =>
              x[0] * SIZE + x[1]
          )
      );

    for (
      let idx = 0;
      idx < inputs.length;
      idx++
    ) {

      const input =
        inputs[idx];

      if (input.disabled) {
        continue;
      }

      input.className =
        'sudoku-cell';

      if (incorrect.has(idx)) {

        input.className =
          'sudoku-cell incorrect';
      }
    }

    if (data.solved) {

      gameSolved = true;

      clearTimer();

      msg.style.color =
        '#388e3c';

      msg.innerText =
        'Congratulations! You solved it!';

      recordSolvedGame();

    } else {

      msg.style.color =
        '#d32f2f';

      if (incorrect.size === 0) {

        msg.innerText =
          'Keep going! Fill all cells correctly.';

      } else {

        msg.innerText =
          'Some cells are incorrect.';
      }
    }

  } catch (error) {

    console.error(
      'Check solution error:',
      error
    );

    const msg =
      document.getElementById(
        'message'
      );

    msg.style.color =
      '#d32f2f';

    msg.innerText =
      'Unable to check the solution.';
  }
}


// --------------------------------------------------
// Page initialization
// --------------------------------------------------

window.addEventListener(
  'load',
  () => {

    initializeTheme();

    const difficultySelect =
      document.getElementById(
        'difficulty-select'
      );

    if (difficultySelect) {

      difficultySelect.addEventListener(
        'change',
        () => {

          updateDifficultyDisplay();

          newGame();
        }
      );
    }

    const themeToggle =
      document.getElementById(
        'theme-toggle'
      );

    if (themeToggle) {

      themeToggle.addEventListener(
        'click',
        () => {

          const nextTheme =
            document.body.dataset.theme === 'dark'
              ? 'light'
              : 'dark';

          applyTheme(nextTheme);
        }
      );
    }

    const newGameButton =
      document.getElementById(
        'new-game'
      );

    if (newGameButton) {

      newGameButton.addEventListener(
        'click',
        newGame
      );
    }

    const checkButton =
      document.getElementById(
        'check-solution'
      );

    if (checkButton) {

      checkButton.addEventListener(
        'click',
        checkSolution
      );
    }

    const hintButton =
      document.getElementById(
        'hint-button'
      );

    if (hintButton) {

      hintButton.addEventListener(
        'click',
        applyHint
      );
    }

    renderScoreboard();
    updateDifficultyDisplay();

    newGame();
  }
);