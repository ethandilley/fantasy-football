import logging
from datetime import datetime

from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.translation import EspnTranslator
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
def silver_team_games():

    @task
    def fetch_games(**context):
        year = context["params"]["year"]
        week = context["params"]["week"]
        print(year)
        print(week)

        minio_client = MinioClient()
        objects = minio_client.fetch_game_objects("bronze", year, week)
        game_paths = [o.object_name for o in objects]
        print(game_paths)

        return game_paths

    @task(multiple_outputs=False)
    def parse_games(game_path: str, **context):
        year = context["params"]["year"]
        week = context["params"]["week"]
        print(year)
        print(week)
        print(game_path)

        minio_client = MinioClient()
        game_info = minio_client.read_data("bronze", game_path)
        print(game_info)

        game_id = int(game_path.split("game=")[1].split("/")[0])
        translator = EspnTranslator()
        teams = translator.to_team_stats(game_id, year, week, game_info)
        print(teams)

        return teams

    @task
    def load(teams_game: list[dict]):
        clickhouse_client = ClickhouseClient()
        clickhouse_client.write_team_game_stats(teams_game)

    game_paths = fetch_games()
    teams_games = parse_games.expand(game_path=game_paths)
    load.expand(teams_game=teams_games)


silver_team_games()
