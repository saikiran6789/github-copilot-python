import pytest

from app import GAMES, app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)

    with app.test_client() as test_client:
        yield test_client

    GAMES.clear()


def test_index_route_returns_html_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Sudoku" in response.data


@pytest.mark.parametrize("clues", [45, 35, 25])
def test_create_puzzle_returns_requested_clue_count(client, clues):
    response = client.post(
        "/api/puzzles",
        json={"clues": clues},
    )

    assert response.status_code == 201

    payload = response.get_json()

    assert "game_id" in payload
    assert "puzzle" in payload
    assert "solution" not in payload
    assert payload["clues"] == clues

    puzzle = payload["puzzle"]

    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)

    filled_cells = sum(
        cell != 0
        for row in puzzle
        for cell in row
    )

    assert filled_cells == clues


def test_current_puzzle_can_be_retrieved(client):
    create_response = client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    created = create_response.get_json()

    response = client.get("/api/puzzles/current")

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["game_id"] == created["game_id"]
    assert payload["puzzle"] == created["puzzle"]
    assert "solution" not in payload


def test_check_requires_active_game(client):
    response = client.post(
        "/api/puzzles/current/check",
        json={"board": [[0] * 9 for _ in range(9)]},
    )

    assert response.status_code == 404


def test_check_reports_incorrect_cells(client):
    create_response = client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    puzzle = create_response.get_json()["puzzle"]

    response = client.post(
        "/api/puzzles/current/check",
        json={"board": puzzle},
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert "incorrect_cells" in payload
    assert "solved" in payload
    assert payload["solved"] is False


def test_abandoning_game_removes_active_session(client):
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    response = client.delete("/api/puzzles/current")

    assert response.status_code == 204

    current = client.get("/api/puzzles/current")

    assert current.status_code == 404