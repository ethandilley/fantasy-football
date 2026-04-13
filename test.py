import gzip
import json
from dataclasses import asdict, dataclass

import clickhouse_connect
from minio import Minio


@dataclass
class PlayerGameStats:
    # identity
    player_id: int
    name: str | None = None
    game_id: int | None = None
    season: int | None = None
    week: int | None = None

    # passing
    passing_attempts: int = 0
    passing_completions: int = 0
    passing_yards: int = 0
    passing_tds: int = 0
    interceptions: int = 0

    # rushing
    rushing_attempts: int = 0
    rushing_yards: int = 0
    rushing_tds: int = 0

    # receiving
    targets: int = 0
    receptions: int = 0
    receiving_yards: int = 0
    receiving_tds: int = 0

    # fumbles
    fumbles: int = 0
    fumbles_lost: int = 0


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
    game_id = int(object_name.split("game=")[1].split("/")[0])
    fileobj = client.get_object("bronze", object_name)
    data = None
    with gzip.GzipFile(fileobj=fileobj) as gz:
        raw_bytes = gz.read()
        data = json.loads(raw_bytes.decode("utf-8"))

    players = {}

    for team in data["boxscore"]["teams"]:
        passing_stats = team["statistics"][0]
        rushing_stats = team["statistics"][1]
        receiving_stats = team["statistics"][2]
        fumble_stats = team["statistics"][3]

        # parse passing
        for athlete in passing_stats["athletes"]:
            player_id = int(athlete["athlete"]["id"])
            player = athlete["athlete"]["displayName"]
            stats = athlete["stats"]
            completions, attempts = stats[0].split("/")
            yards = stats[1]
            touchdowns = stats[3]
            interceptions = stats[4]

            statline = players.get(
                player_id,
                PlayerGameStats(
                    player_id=player_id,
                    name=player,
                    game_id=game_id,
                    season=year,
                    week=week,
                ),
            )
            statline.passing_attempts = int(attempts)
            statline.passing_completions = int(completions)
            statline.passing_yards = int(yards)
            statline.passing_tds = int(touchdowns)
            statline.interceptions = int(interceptions)
            players[player_id] = statline

        # parse rushing
        for athlete in rushing_stats["athletes"]:
            player_id = int(athlete["athlete"]["id"])
            player = athlete["athlete"]["displayName"]
            stats = athlete["stats"]
            attempts = stats[0]
            yards = stats[1]
            tds = stats[3]

            statline = players.get(
                player_id,
                PlayerGameStats(
                    player_id=player_id,
                    name=player,
                    game_id=game_id,
                    season=year,
                    week=week,
                ),
            )
            statline.rushing_attempts = int(attempts)
            statline.rushing_yards = int(yards)
            statline.rushing_tds = int(tds)
            players[player_id] = statline

        for athlete in receiving_stats["athletes"]:
            player_id = int(athlete["athlete"]["id"])
            player = athlete["athlete"]["displayName"]
            stats = athlete["stats"]
            targets = stats[5]
            receptions = stats[0]
            yards = stats[1]
            touchdowns = stats[3]

            statline = players.get(
                player_id,
                PlayerGameStats(
                    player_id=player_id,
                    name=player,
                    game_id=game_id,
                    season=year,
                    week=week,
                ),
            )
            statline.targets = int(targets)
            statline.receptions = int(receptions)
            statline.receiving_yards = int(yards)
            statline.receiving_tds = int(touchdowns)
            players[player_id] = statline

        for athlete in fumble_stats["athletes"]:
            player_id = int(athlete["athlete"]["id"])
            player = athlete["athlete"]["displayName"]
            stats = athlete["stats"]
            fumbles = stats[0]
            lost = stats[1]

            statline = players.get(
                player_id,
                PlayerGameStats(
                    player_id=player_id,
                    name=player,
                    game_id=game_id,
                    season=year,
                    week=week,
                ),
            )
            statline.fumbles = int(fumbles)
            statline.fumbles_lost = int(lost)
            players[player_id] = statline

    # write data
    data = [asdict(p) for p in players.values()]
    print(data)
    clickhouse = clickhouse_connect.get_client(
        host="localhost", port=8123, username="default", password="default"
    )
    columns=[
        "player_id",
        "name",
        "game_id",
        "season",
        "week",
        "passing_attempts",
        "passing_completions",
        "passing_yards",
        "passing_tds",
        "interceptions",
        "rushing_attempts",
        "rushing_yards",
        "rushing_tds",
        "targets",
        "receptions",
        "receiving_yards",
        "receiving_tds",
        "fumbles",
        "fumbles_lost",
    ]
    clickhouse.insert(
        "silver.playergamestats",
        data,
        column_names=columns,
    )
