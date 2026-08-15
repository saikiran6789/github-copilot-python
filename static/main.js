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

function updateDifficultyDisplay() {
  const select = document.getElementById('difficulty-select');
  const display = document.getElementById('current-difficulty');
  const label = select.value.charAt(0).toUpperCase() + select.value.slice(1);
  display.innerText = `Current difficulty: ${label}`;
}

function getSelectedClues() {
  const select = document.getElementById('difficulty-select');
  return DIFFICULTY_TO_CLUES[select.value] || DIFFICULTY_TO_CLUES.medium;
}

function updateTimerDisplay() {
  const timerEl = document.getElementById('timer');
  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;
  timerEl.innerText = `Time: ${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
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
      elapsedSeconds = Math.floor((Date.now() - gameStartedAt) / 1000);
      updateTimerDisplay();
    }
  }, 1000);
}

function applyTheme(theme) {
  const normalizedTheme = theme === 'dark' ? 'dark' : 'light';
  document.body.dataset.theme = normalizedTheme;

  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    const isDark = normalizedTheme === 'dark';
    toggleButton.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    toggleButton.setAttribute('aria-pressed', String(isDark));
    toggleButton.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
  }

  try {
    localStorage.setItem(THEME_STORAGE_KEY, normalizedTheme);
  } catch (error) {
    // Ignore storage errors silently.
  }
}

function initializeTheme() {
  try {
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const defaultTheme = storedTheme || (prefersDark ? 'dark' : 'light');
    applyTheme(defaultTheme);
  } catch (error) {
    applyTheme('light');
  }
}

function hasConflict(board, row, col, value) {
  if (!value) {
    return false;
  }

  for (let i = 0; i < SIZE; i++) {
    if (i !== col && board[row][i] === value) {
      return true;
    }
  }

  for (let i = 0; i < SIZE; i++) {
    if (i !== row && board[i][col] === value) {
      return true;
    }
  }

  const startRow = Math.floor(row / 3) * 3;
  const startCol = Math.floor(col / 3) * 3;
  for (let i = startRow; i < startRow + 3; i++) {
    for (let j = startCol; j < startCol + 3; j++) {
      if ((i !== row || j !== col) && board[i][j] === value) {
        return true;
      }
    }
  }

  return false;
}

function applyImmediateValidation() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = Array.from({length: SIZE}, () => Array(SIZE).fill(0));

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const input = inputs[idx];
      const rawValue = input.value.trim();
      if (rawValue !== '') {
        board[i][j] = parseInt(rawValue, 10);
      }
    }
  }

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const input = inputs[idx];
      if (input.disabled) {
        input.className = input.dataset.hinted === 'true' ? 'sudoku-cell hinted' : 'sudoku-cell prefilled';
        continue;
      }

      const rawValue = input.value.trim();
      const value = rawValue === '' ? 0 : parseInt(rawValue, 10);
      input.className = 'sudoku-cell';
      if (value !== 0 && hasConflict(board, i, j, value)) {
        input.className = 'sudoku-cell incorrect';
      }
    }
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.hinted = 'false';
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      const boxRow = Math.floor(i / 3);
      const boxCol = Math.floor(j / 3);
      const boxVariant = (boxRow + boxCol) % 2 === 0 ? 'var(--cell-box-a)' : 'var(--cell-box-b)';
      input.style.setProperty('--cell-box-bg', boxVariant);
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        applyImmediateValidation();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.dataset.hinted = 'false';
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = 'sudoku-cell';
      }
    }
  }
}

function getStoredScores() {
  try {
    const rawScores = localStorage.getItem(SCOREBOARD_STORAGE_KEY);
    if (!rawScores) {
      return [];
    }
    const parsed = JSON.parse(rawScores);
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter((entry) => {
      return entry && typeof entry.name === 'string' && typeof entry.difficulty === 'string' && Number.isFinite(entry.timeSeconds);
    }).map((entry) => ({
      name: entry.name.trim() || 'Player',
      difficulty: entry.difficulty,
      timeSeconds: Number(entry.timeSeconds)
    }));
  } catch (error) {
    return [];
  }
}

function persistScores(scores) {
  try {
    localStorage.setItem(SCOREBOARD_STORAGE_KEY, JSON.stringify(scores));
  } catch (error) {
    // Ignore storage write failures silently.
  }
}

function renderScoreboard() {
  const scores = getStoredScores()
    .sort((a, b) => a.timeSeconds - b.timeSeconds)
    .slice(0, 10);

  const tableBody = document.getElementById('scoreboard-body');
  const emptyMessage = document.getElementById('scoreboard-empty');
  const table = document.querySelector('.scoreboard-table');
  tableBody.innerHTML = '';

  if (scores.length === 0) {
    table.hidden = true;
    emptyMessage.hidden = false;
    return;
  }

  table.hidden = false;
  emptyMessage.hidden = true;

  scores.forEach((score, index) => {
    const row = document.createElement('tr');
    const minutes = Math.floor(score.timeSeconds / 60);
    const seconds = score.timeSeconds % 60;
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${score.name}</td>
      <td>${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}</td>
      <td>${score.difficulty}</td>
    `;
    tableBody.appendChild(row);
  });
}

function recordSolvedGame() {
  if (scoreSavedForCurrentGame) {
    return;
  }

  const entryName = window.prompt('You solved it! Enter your name for the leaderboard:', 'Player');
  const safeName = (entryName && entryName.trim()) ? entryName.trim().slice(0, 30) : 'Player';
  const scores = getStoredScores();
  scores.push({
    name: safeName,
    difficulty: document.getElementById('difficulty-select').value,
    timeSeconds: elapsedSeconds
  });

  scores.sort((a, b) => a.timeSeconds - b.timeSeconds);
  const topTen = scores.slice(0, 10);
  persistScores(topTen);
  renderScoreboard();
  scoreSavedForCurrentGame = true;
}

function findHintCell() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const input = inputs[idx];
      if (!input.disabled && input.value === '') {
        return { row: i, col: j, input };
      }
    }
  }

  return null;
}

function applyHint() {
  if (gameSolved) {
    document.getElementById('message').innerText = 'This game is already solved.';
    return;
  }

  const hintCell = findHintCell();
  if (!hintCell) {
    const msg = document.getElementById('message');
    msg.style.color = '#d32f2f';
    msg.innerText = 'No empty cells remain.';
    return;
  }

  const { row, col, input } = hintCell;
  const correctValue = currentSolution[row][col];
  input.value = correctValue;
  input.disabled = true;
  input.dataset.hinted = 'true';
  input.className = 'sudoku-cell hinted';
  const msg = document.getElementById('message');
  msg.style.color = '#1f7a1f';
  msg.innerText = 'Hint used!';
}

async function newGame() {
  clearTimer();
  gameSolved = false;
  scoreSavedForCurrentGame = false;
  const clues = getSelectedClues();
  const res = await fetch(`/new?clues=${clues}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  currentSolution = data.solution || [];
  document.getElementById('message').innerText = '';
  updateDifficultyDisplay();
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    gameSolved = true;
    clearTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    recordSolvedGame();
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

window.addEventListener('load', () => {
  initializeTheme();

  const difficultySelect = document.getElementById('difficulty-select');
  difficultySelect.addEventListener('change', () => {
    updateDifficultyDisplay();
  });

  const themeToggle = document.getElementById('theme-toggle');
  themeToggle.addEventListener('click', () => {
    const nextTheme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  });

  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', applyHint);
  renderScoreboard();
  updateDifficultyDisplay();
  newGame();
});