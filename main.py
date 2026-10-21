import os

import requests
from dotenv import load_dotenv

from database import (
    add_game,
    get_game_by_rawg_id,
    initialize_db,
    get_games,
    update_game_status
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


def view_backlog():
    games = get_games()

    if not games:
        print("\nYour backlog is empty.")
        return

    print("\n--- Your Game Backlog ---")

    for game in games:
        print(f"\nID: {game['id']}")
        print(f"Game: {game['name']}")
        print(f"Status: {game['status']}")
        print(f"Release date: {game['released'] or 'Unknown'}")
        print(
            f"Rating: {game['rating'] if game['rating'] is not None else 'Not rated'}")
        print(f"Notes: {game['notes'] or 'None'}")


def change_game_status():
    games = get_games()

    if not games:
        print("\nYour backlog is empty.")
        return

    view_backlog()

    game_id_input = input(
        "\nEnter the ID of the game to update: "
    ).strip()

    try:
        game_id = int(game_id_input)
    except ValueError:
        print("Please enter a valid numeric ID.")
        return

    valid_statuses = [
        "Want to Play",
        "Playing",
        "Completed",
        "Dropped",
    ]

    print("\nChoose a new status:")

    for index, status in enumerate(valid_statuses, start=1):
        print(f"{index}. {status}")

    status_input = input("Enter your choice: ").strip()

    try:
        status_index = int(status_input)
    except ValueError:
        print("Please enter a valid number.")
        return

    if status_index < 1 or status_index > len(valid_statuses):
        print("Invalid status selection.")
        return

    new_status = valid_statuses[status_index - 1]

    updated = update_game_status(game_id, new_status)

    if updated:
        print(f"Game status updated to '{new_status}'.")
    else:
        print(f"No game found with ID {game_id}.")


def main():
    initialize_db()

    while True:
        print("\n=== Game Backlog Tracker ===")
        print("1. Search for and save a game")
        print("2. View my backlog")
        print("3. Change a game's status")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            game_name = input("Enter a game to search for: ")
            games = search_games(game_name)

            if not games:
                continue

            selection = input(
                "\nEnter the number of a game to save, "
                "or press Enter to cancel: "
            ).strip()

            if not selection:
                continue

            try:
                index = int(selection)
            except ValueError:
                print("Please enter a valid number.")
                continue

            if index < 1 or index > len(games):
                print("That number is not in the search results.")
                continue

            save_game(games[index - 1])

        elif choice == "2":
            view_backlog()

        elif choice == "3":
            change_game_status()

        elif choice == "4":
            print("Thanks for using Game Backlog Tracker!")
            break

        else:
            print("Invalid option. Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
