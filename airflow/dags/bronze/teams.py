# get number of total players
# get split it up by page/limit
import logging
from datetime import datetime

from airflow.sdk import dag, task
from utils.minio import MinioClient
from utils.espn import EspnClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    max_active_tasks=5,
)
def bronze_teams():

    @task
    def extract_refs():
        espn_client = EspnClient()
        response = espn_client.get_teams()
        refs = [item["$ref"] for item in response["items"]]
        print(refs)
        return refs

    @task
    def extract_team(ref: str):
        print(ref)
        espn_client = EspnClient()
        response = espn_client._get(ref)
        return response

    @task
    def load(data):
        print(data)
        minio_client = MinioClient()
        object_path = minio_client.get_teams_object_name(data["id"])
        minio_client.write_data("bronze", object_path, data)

    load.expand(data=extract_team.expand(ref=extract_refs()))


bronze_teams()
