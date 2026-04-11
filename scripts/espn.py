import json
import requests

league = "nfl"
season = 2025


def get_player(id: int):
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/{league}/athletes"
    response = requests.get(url)
    print(json.dumps(response.json()))


get_player(10501)
