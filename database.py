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
                image_url TEXT,
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

        # Check whether the image_url column already exists.
        columns = [
            row[1] for row in connection.execute(
                "PRAGMA table_info(games)"
            )
        ]

        # Add it to existing databases if necessary.
        if "image_url" not in columns:
            connection.execute(
                "ALTER TABLE games ADD COLUMN image_url TEXT"
            )


def add_game(
    rawg_id,
    name,
    released=None,
    rating=None,
    image_url=None,
    db_path=DB_PATH
):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO games (
                rawg_id, name, released, rating, image_url
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (rawg_id, name, released, rating, image_url),
        )

        return cursor.lastrowid


def get_games(db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                id,
                rawg_id,
                name,
                released,
                rating,
                image_url,
                status,
                notes
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


def get_game_by_id(game_id, db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            "SELECT * FROM games WHERE id = ?",
            (game_id,),
        ).fetchone()

        return dict(row) if row else None


def get_game_stats(db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row

        total_games = connection.execute(
            "SELECT COUNT(*) FROM games"
        ).fetchone()[0]

        average_rating = connection.execute(
            "SELECT AVG(rating) FROM games"
        ).fetchone()[0]

        status_counts = connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM games
            GROUP BY status
            """
        ).fetchall()

        release_counts = connection.execute(
            """
            SELECT
                COUNT(released) AS with_release_date,
                COUNT(*) - COUNT(released) AS without_release_date
            FROM games
            """
        ).fetchone()

        return {
            "total_games": total_games,
            "average_rating": (
                round(average_rating, 2)
                if average_rating is not None
                else None
            ),
            "games_by_status": {
                row["status"]: row["count"]
                for row in status_counts
            },
            "games_with_release_date": release_counts["with_release_date"],
            "games_without_release_date": release_counts["without_release_date"],
        }


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


def update_game_notes(game_id, notes, db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            "UPDATE games SET notes = ? WHERE id = ?",
            (notes, game_id),
        )

        return cursor.rowcount > 0


def update_game_details(game_id, updates, db_path=DB_PATH):
    allowed_fields = {"name", "released", "rating", "image_url"}

    updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_fields
    }

    if not updates:
        return False

    fields = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values())
    values.append(game_id)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            f"UPDATE games SET {fields} WHERE id = ?",
            values,
        )

        return cursor.rowcount > 0


def delete_game(game_id, db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM games WHERE id = ?",
            (game_id,),
        )

        return cursor.rowcount > 0
