import requests

from main import API_KEY, API_URL
from database import get_games, update_game_details


def update_artwork():
    games = get_games()

    for game in games:
        # Skip games that already have artwork.
        if game.get("image_url"):
            continue

        rawg_id = game.get("rawg_id")

        if not rawg_id:
            print(f"Skipping {game['name']}: missing RAWG ID.")
            continue

        params = {
            "key": API_KEY,
        }

        url = f"https://api.rawg.io/api/games/{rawg_id}"

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            image_url = data.get("background_image")

            if image_url:
                update_game_details(
                    game_id=game["id"],
                    updates={"image_url": image_url},
                )
                print(f"Updated artwork: {game['name']}")
            else:
                print(f"No artwork available: {game['name']}")

        except requests.exceptions.RequestException as error:
            print(f"Could not retrieve {game['name']}: {error}")


if __name__ == "__main__":
    update_artwork()
