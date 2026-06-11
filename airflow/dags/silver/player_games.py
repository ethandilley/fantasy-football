import logging
from datetime import datetime

from airflow.sdk import Param, dag, task
from utils.clickhouse import ClickhouseClient
from utils.minio import MinioClient
from utils.translation import EspnTranslator

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    params={
        "year": Param(2025, type="integer", minimum=1999, maximum=2025),
        "week": Param(1, type="integer", minimum=1, maximum=18),
    },
)
def silver_player_games():

    @task
    def fetch_games(**context):
        year = context["params"]["year"]
        week = context["params"]["week"]

        minio_client = MinioClient()
        objects = minio_client.fetch_game_objects("bronze", year, week)
        game_paths = [o.object_name for o in objects]

        return game_paths

    @task
    def elt(game_path: str, **context):
        year = context["params"]["year"]
        week = context["params"]["week"]

        # extract
        minio_client = MinioClient()
        game_info = minio_client.read_data("bronze", game_path)

        # transform
        game_id = int(game_path.split("game=")[1].split("/")[0])
        espn_client = EspnTranslator()
        players = espn_client.to_player_stats(game_id, year, week, game_info)

        # load
        clickhouse_client = ClickhouseClient()
        clickhouse_client.write_player_game_stats(players)

    elt.expand(game_path=fetch_games())


silver_player_games()
