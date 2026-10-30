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
    assert response.json()["total"] == 2
    assert response.json()["limit"] == 10
    assert response.json()["offset"] == 0
    assert response.json()["games"] == sample_games


def test_list_games_filters_by_status(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?status=Playing")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["games"] == [
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
    assert response.json()["total"] == 1
    assert len(response.json()["games"]) == 1
    assert response.json()["games"][0]["name"] == "Elden Ring"


def test_list_games_returns_empty_list_when_no_games_match(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?status=Dropped")

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["games"] == []


def test_list_games_rejects_invalid_status(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?status=banana")

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid status: banana"


def test_list_games_respects_limit_and_offset(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
        {"id": 3, "name": "Cyberpunk 2077", "status": "Playing"},
        {"id": 4, "name": "Baldur's Gate 3", "status": "Want to Play"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_by=id&limit=2&offset=1")

    assert response.status_code == 200
    assert response.json()["total"] == 4
    assert response.json()["limit"] == 2
    assert response.json()["offset"] == 1
    assert response.json()["games"] == [
        {"id": 2, "name": "Minecraft", "status": "Completed"},
        {"id": 3, "name": "Cyberpunk 2077", "status": "Playing"},
    ]


def test_list_games_uses_default_limit(monkeypatch):
    sample_games = [
        {"id": i, "name": f"Game {i}", "status": "Playing"}
        for i in range(1, 13)
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_by=id")

    assert response.status_code == 200
    assert response.json()["total"] == 12
    assert response.json()["limit"] == 10
    assert response.json()["offset"] == 0
    assert len(response.json()["games"]) == 10
    assert response.json()["games"][0]["name"] == "Game 1"
    assert response.json()["games"][-1]["name"] == "Game 10"


def test_list_games_rejects_invalid_pagination_values():
    invalid_requests = [
        "/games?limit=0",
        "/games?limit=101",
        "/games?offset=-1",
    ]

    for url in invalid_requests:
        response = client.get(url)

        assert response.status_code == 422


def test_list_games_sorts_by_name_ascending(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
        {"id": 3, "name": "Cyberpunk 2077", "status": "Playing"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_by=name&sort_order=asc")

    assert response.status_code == 200

    games = response.json()["games"]

    assert [game["name"] for game in games] == [
        "Cyberpunk 2077",
        "Elden Ring",
        "Minecraft",
    ]


def test_list_games_sorts_by_name_descending(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "status": "Playing"},
        {"id": 2, "name": "Minecraft", "status": "Completed"},
        {"id": 3, "name": "Cyberpunk 2077", "status": "Playing"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_by=name&sort_order=desc")

    assert response.status_code == 200

    games = response.json()["games"]

    assert [game["name"] for game in games] == [
        "Minecraft",
        "Elden Ring",
        "Cyberpunk 2077",
    ]


def test_list_games_sorts_by_rating_ascending(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "rating": 4.5, "status": "Playing"},
        {"id": 2, "name": "Minecraft", "rating": 3.8, "status": "Completed"},
        {"id": 3, "name": "Cyberpunk 2077", "rating": 4.2, "status": "Playing"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_by=rating&sort_order=asc")

    assert response.status_code == 200

    games = response.json()["games"]

    assert [game["rating"] for game in games] == [
        3.8,
        4.2,
        4.5,
    ]


def test_list_games_rejects_invalid_sort_field(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "rating": 4.5, "status": "Playing"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_by=release_date")

    assert response.status_code == 422


def test_list_games_rejects_invalid_sort_order(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "rating": 4.5, "status": "Playing"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_order=random")

    assert response.status_code == 422


def test_list_games_places_unrated_games_last(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "rating": 4.5, "status": "Playing"},
        {"id": 2, "name": "Unknown Game", "rating": None, "status": "Playing"},
        {"id": 3, "name": "Minecraft", "rating": 3.8, "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_by=rating&sort_order=asc")

    assert response.status_code == 200

    games = response.json()["games"]

    assert [game["name"] for game in games] == [
        "Minecraft",
        "Elden Ring",
        "Unknown Game",
    ]


def test_list_games_places_unrated_games_last_descending(monkeypatch):
    sample_games = [
        {"id": 1, "name": "Elden Ring", "rating": 4.5, "status": "Playing"},
        {"id": 2, "name": "Unknown Game", "rating": None, "status": "Playing"},
        {"id": 3, "name": "Minecraft", "rating": 3.8, "status": "Completed"},
    ]

    monkeypatch.setattr("api.get_games", lambda: sample_games)

    response = client.get("/games?sort_by=rating&sort_order=desc")

    assert response.status_code == 200

    games = response.json()["games"]

    assert [game["name"] for game in games] == [
        "Elden Ring",
        "Minecraft",
        "Unknown Game",
    ]


def test_list_games_searches_by_name(monkeypatch):
    monkeypatch.setattr(
        "api.get_games",
        lambda: [
            {"id": 1, "name": "Elden Ring", "rating": 4.5, "status": "Playing"},
            {"id": 2, "name": "The Witcher 3", "rating": 4.8, "status": "Completed"},
            {"id": 3, "name": "Elden Ring Nightreign",
                "rating": 4.0, "status": "Want to Play"},
        ],
    )

    response = client.get("/games?search=ELDEN")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert len(data["games"]) == 2
    assert all("elden" in game["name"].lower() for game in data["games"])


def test_list_games_search_returns_no_matches(monkeypatch):
    monkeypatch.setattr("api.get_games", lambda: [
        {"id": 1, "name": "Elden Ring", "rating": 4.5, "status": "Playing"},
    ])

    response = client.get("/games?search=minecraft")

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["games"] == []


def test_list_games_combines_search_and_status(monkeypatch):
    monkeypatch.setattr("api.get_games", lambda: [
        {"id": 1, "name": "Elden Ring", "rating": 4.5, "status": "Playing"},
        {"id": 2, "name": "Elden Ring Nightreign",
            "rating": 4.0, "status": "Want to Play"},
        {"id": 3, "name": "The Witcher 3", "rating": 4.8, "status": "Playing"},
    ])

    response = client.get("/games?search=elden&status=Playing")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["games"][0]["name"] == "Elden Ring"
