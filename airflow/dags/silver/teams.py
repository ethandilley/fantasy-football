from datetime import datetime, date
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
def teams_silver():

    @task
    def fetch_teams():
        minio_client = MinioClient()
        today = str(date.today())
        objects = minio_client.fetch_team_objects("bronze", today)
        object_names = [o.object_name for o in objects]
        return object_names

    @task
    def extract(object_path: str):
        minio_client = MinioClient()
        team = minio_client.read_data("bronze", object_path)
        return team

    @task
    def transform(team: dict):
        extracted_teams = {}
        name = team.get("name")
        extracted_team = {
            "name": name,
            "espn_id": str(team.get("id", "")),
        }
        extracted_teams[name] = extracted_team
        return [p for p in extracted_teams.values()]

    @task
    def load(teams: list[dict]):
        clickhouse_client = ClickhouseClient()
        clickhouse_client.write_teams(teams)

    load.expand(
        teams=transform.expand(team=extract.expand(object_path=fetch_teams()))
    )


teams_silver()
