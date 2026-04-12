import gzip
import io
import json
import logging
from datetime import datetime

import requests
from airflow.sdk import dag, task
from minio import Minio

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
)
def espn_stats():

    def write_data(bucket, prefix, data):
        client = Minio(
            "minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
        )
        json_bytes = json.dumps(data).encode("utf-8")
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(json_bytes)
        buf.seek(0)
        compressed_data = buf.read()
        client.put_object(
            bucket_name=bucket,
            object_name=prefix,
            data=io.BytesIO(compressed_data),
            length=len(compressed_data),
            content_type="application/gzip",
        )

    @task
    def get_events():
        logger.info("HI")
        year = 2025
        week = 1
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

        object_name = f"espn/raw/events/season={year}/week={week}/data.json.gz"
        write_data("bronze", object_name, response)
        return ids

    @task
    def get_stats(game_id):
        year = 2025
        week = 1
        logger.info(f"processing id: {game_id}")
        # minio path
        # espn/raw/summary/event=401772510/2026-04-11T18:05:12Z.json.gz
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}"
        response = requests.get(url).json()
        object_name = f"espn/raw/stats/season={year}/week={week}/game={game_id}/data.json.gz"
        write_data("bronze", object_name, response)

    ids = get_events()
    get_stats.expand(game_id=ids)


espn_stats()
