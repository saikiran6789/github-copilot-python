import pytest

from app import CURRENT, app


@pytest.fixture(autouse=True)
def reset_current_state():
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    yield
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


def test_index_route_returns_html_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


@pytest.mark.parametrize('clues', [45, 35, 25])
def test_new_game_route_returns_puzzle_and_tracks_current_game(client, clues):
    response = client.get(f'/new?clues={clues}')

    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload['puzzle']) == 9
    assert all(len(row) == 9 for row in payload['puzzle'])
    assert CURRENT['puzzle'] == payload['puzzle']
    assert CURRENT['solution'] is not None
    assert sum(cell == 0 for row in payload['puzzle'] for cell in row) == 81 - clues


def test_check_solution_requires_active_game(client):
    response = client.post('/check', json={'board': [[0 for _ in range(9)] for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json()['error'] == 'No game in progress'


def test_check_solution_reports_incorrect_positions(client):
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    board = [row[:] for row in solution]
    board[0][0] = 8
    CURRENT['solution'] = solution

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 0]]


def test_new_game_route_returns_solution_for_client_hinting(client):
    response = client.get('/new?clues=35')

    assert response.status_code == 200
    payload = response.get_json()
    assert 'solution' in payload
    assert len(payload['solution']) == 9
    assert all(len(row) == 9 for row in payload['solution'])
    assert CURRENT['solution'] == payload['solution']
