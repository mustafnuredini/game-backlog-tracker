import pytest
from fastapi.testclient import TestClient

import api

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
