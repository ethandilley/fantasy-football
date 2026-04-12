import logging
from datetime import datetime

from airflow.sdk import dag, task, Param, get_current_context
from utils.minio import MinioClient
from utils.espn import EspnClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    params={
        "year": Param(2025, type="integer", minimum=2018, maximum=2025),
        "week": Param(1, type="integer", minimum=1, maximum=17),
    },
)
def espn_stats():

    def get_params() -> tuple[int, int]:
        ctx = get_current_context()
        year = ctx["dag"].params["year"]
        week = ctx["dag"].params["week"]
        return year, week

    @task
    def get_events():
        year, week = get_params()
        logger.info(year)

        espn_client = EspnClient()
        response = espn_client.get_events(year, week)
        ids = espn_client.get_event_ids(year, week)

        minio_client = MinioClient()
        object_name = minio_client.get_events_object_name(year, week)
        minio_client.write_data("bronze", object_name, response)
        return ids

    @task
    def get_stats(game_id: str):
        year, week = get_params()

        espn_client = EspnClient()
        response = espn_client.get_stats(game_id)

        minio_client = MinioClient()
        object_name = minio_client.get_stats_object_name(year, week, game_id)
        minio_client.write_data("bronze", object_name, response)

    ids = get_events()
    get_stats.expand(game_id=ids)


espn_stats()
