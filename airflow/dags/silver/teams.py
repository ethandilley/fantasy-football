from datetime import datetime, date, timedelta
import logging

from airflow.sdk import dag, task
from utils.minio import MinioClient
from utils.clickhouse import ClickhouseClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    max_active_tasks=5,
)
def silver_teams():

    @task
    def fetch_teams():
        print("HI")
        minio_client = MinioClient()
        objects = minio_client.fetch_team_objects("bronze")
        print(objects)
        object_names = [o.object_name for o in objects]
        return object_names

    @task
    def elt(object_path: str):
        # extract
        minio_client = MinioClient()
        team = minio_client.read_data("bronze", object_path)
        print(team)

        # transform
        extracted_teams = {}
        name = team.get("name")
        extracted_team = {
            "name": name,
            "espn_id": str(team.get("id", "")),
        }
        extracted_teams[name] = extracted_team

        # load
        teams = [p for p in extracted_teams.values()]
        clickhouse_client = ClickhouseClient()
        clickhouse_client.write_teams(teams)

    elt.expand(object_path=fetch_teams())


silver_teams()
