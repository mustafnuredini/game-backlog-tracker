import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAWG_API_KEY")
API_URL = "https://api.rawg.io/api/games"


def search_games(game_name):
    if not API_KEY:
        print("Error: RAWG_API_KEY is missing from your .env file.")
        return

    if not game_name.strip():
        print("Please enter a game name.")
        return

    params = {
        "key": API_KEY,
        "search": game_name,
        "page_size": 5,
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        print("The request timed out. Please try again.")

    except requests.exceptions.HTTPError as error:
        print(f"API returned an HTTP error: {error}")

    except requests.exceptions.RequestException as error:
        print(f"Could not connect to RAWG: {error}")

    except ValueError:
        print("RAWG returned invalid JSON.")

    else:
        games = data.get("results", [])

        if not games:
            print("No games found.")
            return

        print(f"\nSearch results for '{game_name}':\n")

        for game in games:
            name = game.get("name", "Unknown title")
            released = game.get("released") or "Unknown release date"
            rating = game.get("rating", "Not rated")

            print(f"Game: {name}")
            print(f"Release date: {released}")
            print(f"Rating: {rating}")
            print("-" * 30)


def main():
    print("Welcome to Game Backlog Tracker!")

    game_name = input("Enter a game to search for: ")
    search_games(game_name)


if __name__ == "__main__":
    main()
