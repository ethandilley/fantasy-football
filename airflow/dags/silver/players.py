# get number of total players
# get split it up by page/limit
import logging
from datetime import datetime, date

from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.espn import EspnClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
)
def players():

    @task
    def fetch_pages():
        minio_client = MinioClient()
        object_names = []
        today = str(date.today())
        player_objects = minio_client.fetch_player_objects("bronze", today)
        for player_object in player_objects:
            object_names.append(player_object.object_name)

        return object_names

    @task
    def extract(object_name: str):
        minio_client = MinioClient()
        player_data = minio_client.read_data("bronze", object_name)
        print(player_data)
        return player_data

    @task
    def transform(player_data: dict):
        page, data = result["page"], result["data"]
        print(result)
        minio_client = MinioClient()
        object_name = minio_client.get_players_object_name(page)
        minio_client.write_data("bronze", object_name, data)

    @task
    def load(data: dict):
        pass

    load.expand(result=extract.expand(page=fetch_pages()))


players()
