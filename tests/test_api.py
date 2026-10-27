import pytest
import api
import sqlite3
from fastapi.testclient import TestClient


client = TestClient(api.app)


def test_create_game_success(monkeypatch):
    monkeypatch.setattr(
        api,
        "get_game_by_rawg_id",
        lambda rawg_id: None,
    )
    monkeypatch.setattr(
        api,
        "add_game",
        lambda **kwargs: 1,
    )

    response = client.post(
        "/games",
        json={
            "rawg_id": 999999,
            "name": "Test Game",
            "released": "2025-01-01",
            "rating": 4.2,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Test Game"
    assert response.json()["status"] == "Want to Play"


def test_create_duplicate_game_returns_409(monkeypatch):
    monkeypatch.setattr(
        api,
        "get_game_by_rawg_id",
        lambda rawg_id: {"id": 1, "name": "Test Game"},
    )

    response = client.post(
        "/games",
        json={
            "rawg_id": 999999,
            "name": "Test Game",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "This game is already in your backlog."
    )


def test_create_game_rejects_invalid_data():
    response = client.post(
        "/games",
        json={
            "rawg_id": 999999,
            "name": "",
            "rating": 8,
        },
    )

    assert response.status_code == 422


def test_update_game_status_success(monkeypatch):
    monkeypatch.setattr(
        api,
        "update_game_status",
        lambda game_id, status: True,
    )

    response = client.patch(
        "/games/1",
        json={"status": "Playing"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["status"] == "Playing"


def test_update_nonexistent_game_returns_404(monkeypatch):
    monkeypatch.setattr(
        api,
        "update_game_status",
        lambda game_id, status: False,
    )

    response = client.patch(
        "/games/99999",
        json={"status": "Completed"},
    )

    assert response.status_code == 404


def test_update_game_status_rejects_invalid_status():
    response = client.patch(
        "/games/1",
        json={"status": "In Progress"},
    )

    assert response.status_code == 422


def test_delete_game_success(monkeypatch):
    monkeypatch.setattr(
        api,
        "delete_game",
        lambda game_id: True,
    )

    response = client.delete("/games/1")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Game 1 deleted successfully."
    )


def test_delete_nonexistent_game_returns_404(monkeypatch):
    monkeypatch.setattr(
        api,
        "delete_game",
        lambda game_id: False,
    )

    response = client.delete("/games/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Game with ID 99999 not found."
    )


def test_create_game_rejects_invalid_release_date():
    response = client.post(
        "/games",
        json={
            "rawg_id": 999999,
            "name": "Test Game",
            "released": "not-a-date",
            "rating": 4.2,
        },
    )

    assert response.status_code == 422


def test_create_game_handles_database_duplicate(monkeypatch):
    monkeypatch.setattr(
        api,
        "get_game_by_rawg_id",
        lambda rawg_id: None,
    )

    def raise_integrity_error(**kwargs):
        raise sqlite3.IntegrityError("UNIQUE constraint failed")

    monkeypatch.setattr(
        api,
        "add_game",
        raise_integrity_error,
    )

    response = client.post(
        "/games",
        json={
            "rawg_id": 999999,
            "name": "Test Game",
            "released": "2025-01-01",
            "rating": 4.2,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "This game is already in your backlog."
    )


def test_list_games_returns_all_games(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == sample_games


def test_list_games_filters_by_status(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?status=Playing")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Elden Ring", "status": "Playing"}
    ]


def test_list_games_filters_by_status_case_insensitive(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?status=playing")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Elden Ring"


def test_list_games_returns_empty_list_when_no_games_match(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?status=Dropped")

    assert response.status_code == 200
    assert response.json() == []


def test_list_games_rejects_invalid_status(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?status=banana")

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid status: banana"
