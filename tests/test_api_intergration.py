import pytest
from fastapi.testclient import TestClient

import api
import database


@pytest.fixture
def test_client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_games.db"

    database.initialize_db(db_path)

    # Connect the API to the temporary test database.
    monkeypatch.setattr(
        api,
        "get_games",
        lambda: database.get_games(db_path=db_path),
    )
    monkeypatch.setattr(
        api,
        "get_game_by_rawg_id",
        lambda rawg_id: database.get_game_by_rawg_id(
            rawg_id, db_path=db_path
        ),
    )
    monkeypatch.setattr(
        api,
        "add_game",
        lambda **kwargs: database.add_game(
            **kwargs, db_path=db_path
        ),
    )
    monkeypatch.setattr(
        api,
        "update_game_status",
        lambda game_id, status: database.update_game_status(
            game_id, status, db_path=db_path
        ),
    )
    monkeypatch.setattr(
        api,
        "delete_game",
        lambda game_id: database.delete_game(
            game_id, db_path=db_path
        ),
    )

    return TestClient(api.app)


def test_complete_game_lifecycle(test_client):
    # 1. Create a game.
    create_response = test_client.post(
        "/games",
        json={
            "rawg_id": 987654,
            "name": "Integration Test Game",
            "released": "2025-01-01",
            "rating": 4.5,
        },
    )

    assert create_response.status_code == 201
    game_id = create_response.json()["id"]

    # 2. Retrieve the game.
    list_response = test_client.get("/games")

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert len(list_response.json()["games"]) == 1
    assert list_response.json()["games"][0]["name"] == (
        "Integration Test Game"
    )

    # 3. Update its status.
    update_response = test_client.patch(
        f"/games/{game_id}",
        json={"status": "Playing"},
    )

    assert update_response.status_code == 200

    updated_games = test_client.get("/games").json()
    assert updated_games["games"][0]["status"] == "Playing"

    # 4. Delete the game.
    delete_response = test_client.delete(
        f"/games/{game_id}"
    )

    assert delete_response.status_code == 200
    assert test_client.get("/games").json()["games"] == []


def test_duplicate_game_is_rejected(test_client):
    game_data = {
        "rawg_id": 987654,
        "name": "Integration Test Game",
        "released": "2025-01-01",
        "rating": 4.5,
    }

    first_response = test_client.post(
        "/games",
        json=game_data,
    )

    second_response = test_client.post(
        "/games",
        json=game_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    games = test_client.get("/games").json()
    assert games["total"] == 1
    assert len(games["games"]) == 1
