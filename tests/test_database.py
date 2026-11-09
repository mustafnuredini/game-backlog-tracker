import sqlite3

import pytest

from database import (
    add_game,
    get_games,
    get_game_by_id,
    get_game_stats,
    initialize_db,
    update_game_status,
    update_game_notes,
    update_game_details,
    delete_game
)


@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test_games.db"
    initialize_db(db_path)
    return db_path


def test_add_game(test_db):
    game_id = add_game(
        12345,
        "Elden Ring",
        "2022-02-25",
        4.5,
        db_path=test_db,
    )

    assert game_id == 1


def test_get_games(test_db):
    add_game(12345, "Elden Ring", db_path=test_db)
    add_game(67890, "Baldur's Gate 3", db_path=test_db)

    games = get_games(db_path=test_db)

    assert len(games) == 2
    assert games[0]["name"] == "Baldur's Gate 3"
    assert games[1]["name"] == "Elden Ring"


def test_get_game_by_id(test_db):
    game_id = add_game(
        12345,
        "Elden Ring",
        "2022-02-25",
        4.5,
        db_path=test_db,
    )

    game = get_game_by_id(game_id, db_path=test_db)

    assert game is not None
    assert game["id"] == game_id
    assert game["name"] == "Elden Ring"
    assert game["rawg_id"] == 12345


def test_get_nonexistent_game_by_id(test_db):
    game = get_game_by_id(99999, db_path=test_db)

    assert game is None


def test_duplicate_rawg_id_rejected(test_db):
    add_game(12345, "Elden Ring", db_path=test_db)

    with pytest.raises(sqlite3.IntegrityError):
        add_game(12345, "Duplicate Elden Ring", db_path=test_db)


def test_update_game_status(test_db):
    game_id = add_game(
        12345,
        "Elden Ring",
        db_path=test_db,
    )

    result = update_game_status(
        game_id,
        "Playing",
        db_path=test_db,
    )

    assert result is True

    games = get_games(db_path=test_db)
    assert games[0]["status"] == "Playing"


def test_update_game_status_rejects_invalid_status(test_db):
    game_id = add_game(
        12345,
        "Elden Ring",
        db_path=test_db,
    )

    with pytest.raises(ValueError):
        update_game_status(
            game_id,
            "In Progress",
            db_path=test_db,
        )


def test_delete_game(test_db):
    game_id = add_game(12345, "Elden Ring", db_path=test_db)

    result = delete_game(game_id, db_path=test_db)

    assert result is True
    assert get_games(db_path=test_db) == []


def test_delete_nonexistent_game(test_db):
    result = delete_game(99999, db_path=test_db)

    assert result is False


def test_update_game_notes(test_db):
    game_id = add_game(
        12345,
        "Elden Ring",
        db_path=test_db,
    )

    result = update_game_notes(
        game_id,
        "Play with friends.",
        db_path=test_db,
    )

    assert result is True

    game = get_game_by_id(game_id, db_path=test_db)
    assert game["notes"] == "Play with friends."


def test_update_nonexistent_game_notes(test_db):
    result = update_game_notes(
        99999,
        "Some notes",
        db_path=test_db,
    )

    assert result is False


def test_update_game_details_single_field(test_db):
    game_id = add_game(
        3498,
        "Grand Theft Auto V",
        "2013-09-17",
        4.5,
        db_path=test_db,
    )

    update_game_details(
        game_id,
        {"rating": 4.8},
        db_path=test_db,
    )

    game = get_game_by_id(game_id, db_path=test_db)

    assert game["rating"] == 4.8
    assert game["name"] == "Grand Theft Auto V"
    assert game["released"] == "2013-09-17"


def test_update_game_details_multiple_fields(test_db):
    game_id = add_game(
        3498,
        "Grand Theft Auto V",
        "2013-09-17",
        4.5,
        db_path=test_db,
    )

    update_game_details(
        game_id,
        {"name": "GTA V", "rating": 4.9},
        db_path=test_db,
    )

    game = get_game_by_id(game_id, db_path=test_db)

    assert game["name"] == "GTA V"
    assert game["rating"] == 4.9


def test_update_game_details_game_not_found(test_db):
    result = update_game_details(
        999,
        {"rating": 4.8},
        db_path=test_db,
    )

    assert result is False


def test_get_game_stats(test_db):
    add_game(3498, "GTA V", "2013-09-17", 4.5, db_path=test_db)
    add_game(3328, "The Witcher 3", "2015-05-18", 5.0, db_path=test_db)
    add_game(9999, "Unreleased Game", None, None, db_path=test_db)

    stats = get_game_stats(db_path=test_db)

    assert stats["total_games"] == 3
    assert stats["average_rating"] == 4.75
    assert stats["games_by_status"] == {
        "Want to Play": 3
    }
    assert stats["games_with_release_date"] == 2
    assert stats["games_without_release_date"] == 1


def test_get_game_stats_empty_database(test_db):
    stats = get_game_stats(db_path=test_db)

    assert stats["total_games"] == 0
    assert stats["average_rating"] is None
    assert stats["games_by_status"] == {}
    assert stats["games_with_release_date"] == 0
    assert stats["games_without_release_date"] == 0


def test_get_game_stats_different_statuses(test_db):
    game1 = add_game(3498, "GTA V", db_path=test_db)
    game2 = add_game(3328, "The Witcher 3", db_path=test_db)

    update_game_status(game1, "Playing", db_path=test_db)
    update_game_status(game2, "Completed", db_path=test_db)

    stats = get_game_stats(db_path=test_db)

    assert stats["games_by_status"] == {
        "Playing": 1,
        "Completed": 1,
    }
