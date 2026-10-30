from fastapi import FastAPI, HTTPException, Query
from database import get_games, get_game_by_rawg_id, add_game, update_game_status, delete_game
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date
import sqlite3

app = FastAPI(
    title="Game Backlog Tracker API",
    description="An API for managing your personal video game backlog.",
    version="1.0.0",
)


class GameCreate(BaseModel):
    rawg_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=200)
    released: date | None = None
    rating: float | None = Field(default=None, ge=0, le=5)


class GameStatusUpdate(BaseModel):
    status: Literal[
        "Want to Play",
        "Playing",
        "Completed",
        "Dropped",
    ]


@app.get("/")
def home():
    return {"message": "Welcome to Game Backlog Tracker API!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/games")
def list_games(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    sort_by: str = Query(default="name"),
    sort_order: str = Query(default="asc"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    games = get_games()

    if search is not None:
        search_term = search.strip().lower()

        if search_term:
            games = [
                game
                for game in games
                if search_term in game["name"].lower()
            ]

    valid_sort_fields = ["id", "name", "rating"]
    valid_sort_orders = ["asc", "desc"]

    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid sort field: {sort_by}",
        )

    if sort_order.lower() not in valid_sort_orders:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid sort order: {sort_order}",
        )

    if status is not None:
        valid_statuses = [
            "Want to Play",
            "Playing",
            "Completed",
            "Dropped",
        ]

        matching_status = next(
            (
                valid_status
                for valid_status in valid_statuses
                if valid_status.lower() == status.lower()
            ),
            None,
        )

        if matching_status is None:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status: {status}",
            )

        games = [
            game
            for game in games
            if game["status"] == matching_status
        ]

    total = len(games)

    if sort_order.lower() == "desc":
        games = sorted(
            games,
            key=lambda game: (
                game[sort_by] is None,
                game[sort_by] if game[sort_by] is not None else 0
            ),
        )

        games = sorted(
            games,
            key=lambda game: (
                game[sort_by] is not None,
                game[sort_by] if game[sort_by] is not None else 0
            ),
            reverse=True,
        )

    else:
        games = sorted(
            games,
            key=lambda game: (
                game[sort_by] is None,
                game[sort_by] if game[sort_by] is not None else 0
            ),
        )

    paginated_games = games[offset:offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "games": paginated_games,
    }


@app.post("/games", status_code=201)
def create_game(game: GameCreate):
    existing_game = get_game_by_rawg_id(game.rawg_id)

    if existing_game:
        raise HTTPException(
            status_code=409,
            detail="This game is already in your backlog.",
        )

    try:
        game_id = add_game(
            rawg_id=game.rawg_id,
            name=game.name.strip(),
            released=(
                game.released.isoformat()
                if game.released
                else None
            ),
            rating=game.rating,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="This game is already in your backlog.",
        )

    return {
        "id": game_id,
        "rawg_id": game.rawg_id,
        "name": game.name.strip(),
        "released": game.released.isoformat() if game.released else None,
        "rating": game.rating,
        "status": "Want to Play",
        "notes": "",
    }


@app.patch("/games/{game_id}")
def update_status(game_id: int, update: GameStatusUpdate):
    updated = update_game_status(game_id, update.status)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Game with ID {game_id} not found.",
        )

    return {
        "id": game_id,
        "status": update.status,
        "message": "Game status updated successfully.",
    }


@app.delete("/games/{game_id}")
def remove_game(game_id: int):
    deleted = delete_game(game_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Game with ID {game_id} not found.",
        )

    return {"message": f"Game {game_id} deleted successfully."}
