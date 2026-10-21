import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "games.db"


def initialize_db(db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rawg_id INTEGER UNIQUE,
                name TEXT NOT NULL,
                released TEXT,
                rating REAL,
                status TEXT NOT NULL DEFAULT 'Want to Play'
                    CHECK (
                        status IN (
                            'Want to Play',
                            'Playing',
                            'Completed',
                            'Dropped'
                        )
                    ),
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_game(rawg_id, name, released=None, rating=None, db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO games (rawg_id, name, released, rating)
            VALUES (?, ?, ?, ?)
            """,
            (rawg_id, name, released, rating),
        )

        return cursor.lastrowid


def get_games(db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT id, rawg_id, name, released, rating, status, notes
            FROM games
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()

        return [dict(row) for row in rows]


def get_game_by_rawg_id(rawg_id, db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            "SELECT * FROM games WHERE rawg_id = ?",
            (rawg_id,),
        ).fetchone()

        return dict(row) if row else None


def update_game_status(game_id, status, db_path=DB_PATH):
    allowed_statuses = {
        "Want to Play",
        "Playing",
        "Completed",
        "Dropped",
    }

    if status not in allowed_statuses:
        raise ValueError(f"Invalid game status: {status}")

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            "UPDATE games SET status = ? WHERE id = ?",
            (status, game_id),
        )

        return cursor.rowcount > 0
