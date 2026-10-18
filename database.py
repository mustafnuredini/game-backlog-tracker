
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "games.db"


def initialize_db():
    with sqlite3.connect(DB_PATH) as connection:
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
