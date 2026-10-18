import sqlite3

import pytest

from database import add_game, get_games, initialize_db


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


def test_duplicate_rawg_id_rejected(test_db):
    add_game(12345, "Elden Ring", db_path=test_db)

    with pytest.raises(sqlite3.IntegrityError):
        add_game(12345, "Duplicate Elden Ring", db_path=test_db)
