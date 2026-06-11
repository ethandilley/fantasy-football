import logging
from datetime import datetime

from airflow.sdk import dag, task
from utils.minio import MinioClient
from utils.espn import EspnClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
)
def bronze_teams():

    @task
    def extract_refs():
        espn_client = EspnClient()
        response = espn_client.get_teams()
        refs = [item["$ref"] for item in response["items"]]
        logger.info(refs)
        return refs

    @task
    def extract_and_load_team(ref: str):
        logger.info(ref)
        espn_client = EspnClient()
        data = espn_client._get(ref)

        minio_client = MinioClient()
        object_path = minio_client.get_teams_object_name(data["id"])
        minio_client.write_data("bronze", object_path, data)

    extract_and_load_team.expand(ref=extract_refs())


bronze_teams()
