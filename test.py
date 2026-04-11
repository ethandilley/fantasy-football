from datetime import datetime
import json
import io
from minio import Minio
import requests
import gzip


client = Minio(
    "localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
)
bucket = "bronze"


def get_event_ids_by_week(year: int, week: int):
    # "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?seasontype=2&week=1&year=2025" | jq ".events[].competitions[].id"

    # "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/types/2/weeks/1/events" \

    # "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=401772510"

    ids = []
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/types/2/weeks/{week}/events"
    response = requests.get(url).json()
    for item in response["items"]:
        game_id = (
            item["$ref"]
            .strip(
                "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/"
            )
            .strip("?lang=en&region=us")
        )
        ids.append(game_id)
    return ids


# print(get_event_ids_by_week(2018, 1))


def get_events_ids_by_week_raw(year: int, week: int):
    # minio path
    # espn/raw/events/season=2024/week=2/2026-04-11T18:05:12Z.json.gz
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/types/2/weeks/{week}/events"
    response = requests.get(url).json()
    json_bytes = json.dumps(response).encode("utf-8")
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(json_bytes)
    buf.seek(0)
    compressed_data = buf.read()
    now = datetime.now()
    object_name = f"espn/raw/events/season={year}/week={week}/{now}.json.gz"
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=io.BytesIO(compressed_data),
        length=len(compressed_data),
        content_type="application/gzip",
    )


# get_events_ids_by_week_raw(2018, 1)


def get_stats_by_game_id(year: int, week: int, game_id: int):
    # minio path
    # espn/raw/summary/event=401772510/2026-04-11T18:05:12Z.json.gz
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}"
    response = requests.get(url).json()
    print(json.dumps(response))
    # compress response into json.gz and load into minio at above path (after building the path)

    json_bytes = json.dumps(response).encode("utf-8")
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(json_bytes)
    buf.seek(0)
    compressed_data = buf.read()
    now = datetime.now()
    object_name = f"espn/raw/summary/season={year}/week={week}/game={game_id}/{now}.json.gz"
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=io.BytesIO(compressed_data),
        length=len(compressed_data),
        content_type="application/gzip",
    )


get_stats_by_game_id(2024, 1, 401030721)
