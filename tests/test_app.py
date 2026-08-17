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


# ==================== API VALIDATION TESTS ====================

def test_create_puzzle_rejects_invalid_clue_count(client):
    """Test that unsupported clue counts return HTTP 400."""
    response = client.post(
        "/api/puzzles",
        json={"clues": 50},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload


def test_create_puzzle_rejects_non_integer_clues(client):
    """Test that non-integer clue counts return HTTP 400."""
    response = client.post(
        "/api/puzzles",
        json={"clues": "abc"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload


def test_create_puzzle_defaults_to_medium(client):
    """Test that missing clues parameter defaults to 35."""
    response = client.post("/api/puzzles")

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["clues"] == 35


def test_check_requires_valid_json(client):
    """Test that missing JSON body returns HTTP 400."""
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    response = client.post(
        "/api/puzzles/current/check",
        data="invalid",
        content_type="text/plain",
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload


def test_check_requires_board_field(client):
    """Test that missing 'board' field returns HTTP 400."""
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    response = client.post(
        "/api/puzzles/current/check",
        json={"some_field": "value"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload
    assert "board" in payload["error"]


def test_check_requires_board_to_be_list(client):
    """Test that non-list board returns HTTP 400."""
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    response = client.post(
        "/api/puzzles/current/check",
        json={"board": "not a list"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload


def test_check_requires_9x9_board(client):
    """Test that non-9x9 board returns HTTP 400."""
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    response = client.post(
        "/api/puzzles/current/check",
        json={"board": [[0] * 8 for _ in range(9)]},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload


def test_check_requires_9_rows(client):
    """Test that board without 9 rows returns HTTP 400."""
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    response = client.post(
        "/api/puzzles/current/check",
        json={"board": [[0] * 9 for _ in range(8)]},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload
    assert "9 rows" in payload["error"]


def test_check_requires_integer_cells(client):
    """Test that non-integer cells return HTTP 400."""
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    board = [[0] * 9 for _ in range(9)]
    board[0][0] = "not an int"

    response = client.post(
        "/api/puzzles/current/check",
        json={"board": board},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload
    assert "integer" in payload["error"]


def test_check_requires_cells_between_0_and_9(client):
    """Test that cells outside 0-9 range return HTTP 400."""
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 10

    response = client.post(
        "/api/puzzles/current/check",
        json={"board": board},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload
    assert "between 0 and 9" in payload["error"]


def test_hint_returns_hints_used_counter(client):
    """Test that hint endpoint returns hints_used counter."""
    create_response = client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    hint_response = client.post(
        "/api/puzzles/current/hint",
    )

    assert hint_response.status_code == 200
    payload = hint_response.get_json()
    assert "hints_used" in payload
    assert payload["hints_used"] == 1


def test_hint_increments_counter(client):
    """Test that multiple hints increment the counter."""
    client.post(
        "/api/puzzles",
        json={"clues": 25},  # Hard puzzle has 56 empty cells
    )

    response1 = client.post("/api/puzzles/current/hint")
    assert response1.get_json()["hints_used"] == 1

    response2 = client.post("/api/puzzles/current/hint")
    assert response2.get_json()["hints_used"] == 2

    response3 = client.post("/api/puzzles/current/hint")
    assert response3.get_json()["hints_used"] == 3


def test_get_current_puzzle_includes_metadata(client):
    """Test that get current puzzle returns hints_used and difficulty."""
    client.post(
        "/api/puzzles",
        json={"clues": 45},
    )

    response = client.get("/api/puzzles/current")

    assert response.status_code == 200
    payload = response.get_json()
    assert "hints_used" in payload
    assert payload["hints_used"] == 0
    assert "difficulty" in payload
    assert payload["difficulty"] == "Easy"


def test_solution_never_exposed_in_check_response(client):
    """Verify that solution is never included in check response."""
    client.post(
        "/api/puzzles",
        json={"clues": 35},
    )

    response = client.post(
        "/api/puzzles/current/check",
        json={"board": [[0] * 9 for _ in range(9)]},
    )

    payload = response.get_json()
    assert "solution" not in payload