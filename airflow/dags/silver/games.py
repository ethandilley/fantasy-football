import logging
from datetime import datetime

from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.clickhouse import ClickhouseClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    params={
        "year": Param(2025, type="integer", minimum=1999, maximum=2025),
        "week": Param(1, type="integer", minimum=1, maximum=18),
    },
)
def games_silver():

    @task
    def fetch_games(**context):
        year = context["params"]["year"]
        week = context["params"]["week"]

        minio_client = MinioClient()
        objects = minio_client.fetch_game_objects("bronze", year, week)
        return [o.object_name for o in objects]

    @task(multiple_outputs=False)
    def extract(game_path: str) -> dict:
        print(game_path)
        minio_client = MinioClient()
        game_info = minio_client.read_data("bronze", game_path)
        return game_info

    @task
    def transform(data):
        print(data)

        header = data.get("header") or {}
        season = header.get("season") or {}
        competitions = header.get("competitions")[0]
        home_team, away_team = competitions.get("competitors")

        extracted_data = {
            "espn_id": int(header.get("id")),
            "slug": f"{home_team.get('team').get('displayName')}-{away_team.get('team').get('displayName')}",
            "season": int(season.get("year")),
            "week": int(header.get("week")),
            "home_team_id": int(home_team.get("id")),
            "away_team_id": int(away_team.get("id")),
            "home_score": int(home_team.get("score")),
            "away_score": int(away_team.get("score")),
            "game_date": competitions.get("date"),
            "weather_condition": "sunny",
            "temperature": 70,
            "wind_speed": 5,
        }

        return extracted_data

    @task
    def load(data):
        print(data)
        clickhouse_client = ClickhouseClient()
        clickhouse_client.write_games(data)

    game_paths = fetch_games()
    load.expand(data=transform.expand(data=extract.expand(game_path=game_paths)))


games_silver()
