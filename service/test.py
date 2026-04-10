import requests
import json

def get_all_players():
    players = []
    endpoint = "seasons/20255/athletes"
    response = requests.get(base_url + endpoint)
    print(json.dumps(response.json()))

# base_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/"
#
# endpoint = "seasons/2025/athletes"
#
#
# response = requests.get(base_url + endpoint)
# print(json.dumps(response.json()))
