import os

import requests
from dotenv import load_dotenv

from database import (
    add_game,
    get_game_by_rawg_id,
    initialize_db,
)

load_dotenv()

API_KEY = os.getenv("RAWG_API_KEY")
API_URL = "https://api.rawg.io/api/games"


def search_games(game_name):
    if not API_KEY:
        print("Error: RAWG_API_KEY is missing from your .env file.")
        return []

    if not game_name.strip():
        print("Please enter a game name.")
        return []

    params = {
        "key": API_KEY,
        "search": game_name,
        "page_size": 5,
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        print("The request timed out. Please try again.")
        return []

    except requests.exceptions.HTTPError as error:
        print(f"API returned an HTTP error: {error}")
        return []

    except requests.exceptions.RequestException as error:
        print(f"Could not connect to RAWG: {error}")
        return []

    except ValueError:
        print("RAWG returned invalid JSON.")
        return []

    games = data.get("results", [])

    if not games:
        print("No games found.")
        return []

    print(f"\nSearch results for '{game_name}':\n")

    for index, game in enumerate(games, start=1):
        name = game.get("name", "Unknown title")
        released = game.get("released") or "Unknown release date"
        rating = game.get("rating", "Not rated")

        print(f"{index}. {name}")
        print(f"   Release date: {released}")
        print(f"   Rating: {rating}")

    return games


def save_game(game):
    rawg_id = game.get("id")

    if rawg_id is None:
        print("Cannot save this game: RAWG ID is missing.")
        return

    existing_game = get_game_by_rawg_id(rawg_id)

    if existing_game:
        print(f"{game.get('name', 'This game')} is already in your backlog.")
        return

    try:
        game_id = add_game(
            rawg_id=rawg_id,
            name=game.get("name", "Unknown title"),
            released=game.get("released"),
            rating=game.get("rating"),
        )
    except Exception as error:
        print(f"Could not save game: {error}")
        return

    print(f"Saved {game.get('name', 'game')} to your backlog! (ID: {game_id})")


def main():
    initialize_db()

    print("Welcome to Game Backlog Tracker!")
    game_name = input("Enter a game to search for: ")

    games = search_games(game_name)

    if not games:
        return

    choice = input(
        "\nEnter the number of a game to save it, "
        "or press Enter to exit: "
    ).strip()

    if not choice:
        print("No game saved.")
        return

    try:
        index = int(choice)
    except ValueError:
        print("Please enter a valid number.")
        return

    if index < 1 or index > len(games):
        print("That number is not in the search results.")
        return

    save_game(games[index - 1])


if __name__ == "__main__":
    main()
