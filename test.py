from minio import Minio
from dataclasses import dataclass
import json
import gzip


@dataclass
class PlayerGameStats:
    # identity
    player_id: int
    game_id: int | None
    season: int | None
    week: int | None
    team_id: int | None
    opponent_team_id: int | None

    # passing
    passing_attempts: int | None
    passing_completions: int | None
    passing_yards: int | None
    passing_tds: int | None
    interceptions: int | None

    # rushing
    rushing_attempts: int | None
    rushing_yards: int | None
    rushing_tds: int | None

    # receiving
    targets: int | None
    receptions: int | None
    receiving_yards: int | None
    receiving_tds: int | None

    # fumbles
    fumbles: int | None
    fumbles_lost: int | None


year = 2025
week = 1

# task to get game data from minio
client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

prefix = "espn/raw/stats/season=2025/week=1/"

objects = client.list_objects(
    bucket_name="bronze",
    prefix=prefix,
    recursive=True,
)

object_names = []
for o in objects:
    object_names.append(o.object_name)
object_names = object_names[:1]


# parse data
for object_name in object_names:
    fileobj = client.get_object("bronze", object_name)
    data = None
    with gzip.GzipFile(fileobj=fileobj) as gz:
        raw_bytes = gz.read()
        data = json.loads(raw_bytes.decode("utf-8"))

    for team in data["boxscore"]["players"]:
        passing_stats = team["statistics"][0]
        rushing_stats = team["statistics"][1]
        receiving_stats = team["statistics"][2]
        fumble_stats = team["statistics"][3]

        # parse passing
        for athlete in passing_stats["athletes"]:
            player_id = athlete["athlete"]["id"]
            player = athlete["athlete"]["displayName"]
            stats = athlete["stats"]
            print(player_id)
            print(player)
            print(stats)
            


{
    "name": "passing",
    "keys": [
        "completions/passingAttempts",
        "passingYards",
        "yardsPerPassAttempt",
        "passingTouchdowns",
        "interceptions",
        "sacks-sackYardsLost",
        "adjQBR",
        "QBRating",
    ],
    "text": "Philadelphia Passing",
    "labels": ["C/ATT", "YDS", "AVG", "TD", "INT", "SACKS", "QBR", "RTG"],
    "descriptions": [
        "Completions/Attempts",
        "Yards",
        "Yards Per Pass Attempt",
        "Touchdowns",
        "Interceptions",
        "Sacks",
        "Adjusted QBR",
        "Passer Rating",
    ],
    "athletes": [
        {
            "athlete": {
                "id": "4040715",
                "uid": "s:20~l:28~a:4040715",
                "guid": "caceb80c-6350-a107-9fcf-7c7bd1b4edd8",
                "firstName": "Jalen",
                "lastName": "Hurts",
                "displayName": "Jalen Hurts",
                "links": [
                    {
                        "rel": ["playercard", "desktop", "athlete"],
                        "href": "https://www.espn.com/nfl/player/_/id/4040715/jalen-hurts",
                        "text": "Player Card",
                    }
                ],
                "headshot": {
                    "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4040715.png",
                    "alt": "Jalen Hurts",
                },
                "jersey": "1",
            },
            "stats": ["19/23", "152", "6.6", "0", "0", "1-8", "89.0", "94.2"],
        }
    ],
    "totals": ["19/23", "144", "6.6", "0", "0", "1-8", "--", "94.2"],
}
