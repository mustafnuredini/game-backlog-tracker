from fastapi import FastAPI, HTTPException
from database import get_games, get_game_by_rawg_id, add_game, update_game_status, delete_game
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

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
def list_games():
    return get_games()


@app.post("/games", status_code=201)
def create_game(game: GameCreate):
    existing_game = get_game_by_rawg_id(game.rawg_id)

    if existing_game:
        raise HTTPException(
            status_code=409,
            detail="This game is already in your backlog.",
        )

    game_id = add_game(
        rawg_id=game.rawg_id,
        name=game.name.strip(),
        released=game.released.isoformat() if game.released else None,
        rating=game.rating,
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
