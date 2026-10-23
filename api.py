from fastapi import FastAPI
from database import get_games

app = FastAPI(
    title="Game Backlog Tracker API",
    description="An API for managing your personal video game backlog.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "Welcome to Game Backlog Tracker API!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/games")
def list_games():
    return get_games()
