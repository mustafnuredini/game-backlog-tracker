import os
import sqlite3
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

DB_PATH = Path(__file__).resolve().parent / "games.db"


def get_connection(db_path=DB_PATH):
    database_url = os.getenv("DATABASE_URL")

    if database_url and db_path == DB_PATH:
        return psycopg.connect(
            database_url,
            row_factory=dict_row,
        )

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def execute_query(connection, query, params=()):
    if isinstance(connection, psycopg.Connection):
        query = query.replace("?", "%s")

    return connection.execute(query, params)


def initialize_db(db_path=DB_PATH):
    with get_connection(db_path) as connection:

        if isinstance(connection, psycopg.Connection):
            connection.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id SERIAL PRIMARY KEY,
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
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.execute("""
                ALTER TABLE games
                ADD COLUMN IF NOT EXISTS image_url TEXT
            """)

        else:
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

            columns = [
                row["name"] for row in connection.execute(
                    "PRAGMA table_info(games)"
                )
            ]

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
    with get_connection(db_path) as connection:
        cursor = execute_query(
            connection,
            """
            INSERT INTO games (
                rawg_id, name, released, rating, image_url
            )
            VALUES (?, ?, ?, ?, ?)
            RETURNING id
            """,
            (rawg_id, name, released, rating, image_url),
        )

        return cursor.fetchone()["id"]


def get_games(db_path=DB_PATH):
    with get_connection(db_path) as connection:
        rows = execute_query(
            connection,
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
            ORDER BY LOWER(name)
            """
        ).fetchall()

        return [dict(row) for row in rows]


def get_game_by_rawg_id(rawg_id, db_path=DB_PATH):
    with get_connection(db_path) as connection:
        row = execute_query(
            connection,
            "SELECT * FROM games WHERE rawg_id = ?",
            (rawg_id,),
        ).fetchone()

        return dict(row) if row else None


def get_game_by_id(game_id, db_path=DB_PATH):
    with get_connection(db_path) as connection:
        row = execute_query(
            connection,
            "SELECT * FROM games WHERE id = ?",
            (game_id,),
        ).fetchone()

        return dict(row) if row else None


def get_game_stats(db_path=DB_PATH):
    with get_connection(db_path) as connection:

        total_games = connection.execute(
            "SELECT COUNT(*) AS total_games FROM games"
        ).fetchone()["total_games"]

        average_rating = connection.execute(
            "SELECT AVG(rating) AS average_rating FROM games"
        ).fetchone()["average_rating"]

        games_with_release_date = connection.execute("""
            SELECT COUNT(*) AS games_with_release_date
            FROM games
            WHERE released IS NOT NULL
            AND released != ''
        """).fetchone()["games_with_release_date"]

        games_without_release_date = connection.execute("""
            SELECT COUNT(*) AS games_without_release_date
            FROM games
            WHERE released IS NULL
            OR released = ''
        """).fetchone()["games_without_release_date"]

        status_counts = connection.execute("""
            SELECT status, COUNT(*) AS count
            FROM games
            GROUP BY status
        """).fetchall()

        release_counts = connection.execute("""
            SELECT
                SUBSTR(released, 1, 4) AS year,
                COUNT(*) AS count
            FROM games
            WHERE released IS NOT NULL
              AND released != ''
            GROUP BY year
            ORDER BY year
        """).fetchall()

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
            "release_counts": {
                row["year"]: row["count"]
                for row in release_counts
            },
            "games_with_release_date": games_with_release_date,
            "games_without_release_date": games_without_release_date,
        }


def update_game_status(game_id, status, db_path=DB_PATH):
    valid_statuses = {
        "Want to Play",
        "Playing",
        "Completed",
        "Dropped",
    }

    if status not in valid_statuses:
        raise ValueError("Invalid game status")

    with get_connection(db_path) as connection:
        cursor = execute_query(
            connection,
            """
            UPDATE games
            SET status = ?
            WHERE id = ?
            """,
            (status, game_id),
        )

        return cursor.rowcount > 0


def update_game_notes(game_id, notes, db_path=DB_PATH):
    with get_connection(db_path) as connection:
        cursor = execute_query(
            connection,
            """
            UPDATE games
            SET notes = ?
            WHERE id = ?
            """,
            (notes, game_id),
        )

        return cursor.rowcount > 0


def update_game_details(game_id, updates, db_path=DB_PATH):
    if not updates:
        return False

    allowed_fields = {
        "name",
        "released",
        "rating",
        "image_url",
        "status",
        "notes",
    }

    if "status" in updates:
        valid_statuses = {
            "Want to Play",
            "Playing",
            "Completed",
            "Dropped",
        }

        if updates["status"] not in valid_statuses:
            raise ValueError("Invalid game status")

    if not set(updates).issubset(allowed_fields):
        raise ValueError("Invalid field in updates")

    fields = ", ".join(
        f"{field} = ?" for field in updates
    )

    values = list(updates.values())
    values.append(game_id)

    with get_connection(db_path) as connection:
        cursor = execute_query(
            connection,
            f"""
            UPDATE games
            SET {fields}
            WHERE id = ?
            """,
            values,
        )

        return cursor.rowcount > 0


def delete_game(game_id, db_path=DB_PATH):
    with get_connection(db_path) as connection:
        cursor = execute_query(
            connection,
            "DELETE FROM games WHERE id = ?",
            (game_id,),
        )

        return cursor.rowcount > 0
