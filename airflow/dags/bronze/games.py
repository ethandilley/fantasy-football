import logging
from datetime import datetime

from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.espn import EspnClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    params={
        "year": Param(2025, type="integer", minimum=1999, maximum=2025),
        "week": Param(1, type="integer", minimum=1, maximum=18),
    },
)
def bronze_games():

    @task
    def get_events(**context):
        year = context["params"]["year"]
        week = context["params"]["week"]

        logger.info(year)

        espn_client = EspnClient()
        response = espn_client.get_events(year, week)
        ids = espn_client.get_event_ids(year, week)

        minio_client = MinioClient()
        object_name = minio_client.get_events_object_name(year, week)
        print(response)
        minio_client.write_data("bronze", object_name, response)
        return ids

    @task
    def get_stats(game_id: str, **context):
        year = context["params"]["year"]
        week = context["params"]["week"]

        espn_client = EspnClient()
        response = espn_client.get_stats(game_id)

        minio_client = MinioClient()
        object_name = minio_client.get_stats_object_name(year, week, game_id)
        print(response)
        minio_client.write_data("bronze", object_name, response)

    ids = get_events()
    get_stats.expand(game_id=ids)


bronze_games()
