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
def silver_players():

    @task
    def fetch_players():
        minio_client = MinioClient()
        today = str(date.today())
        objects = minio_client.fetch_player_objects("bronze", today)
        object_names = [o.object_name for o in objects]
        return object_names

    @task
    def extract(object_path: str):
        minio_client = MinioClient()
        players = minio_client.read_data("bronze", object_path)
        return {"players": players}

    @task
    def transform(results: dict):
        players = results["players"]
        extracted_players = {}
        for player in players:
            name = player.get("displayName")
            draft = player.get("draft") or {}
            status = player.get("status") or {}
            extracted_player = {
                "name": name,
                "espn_id": str(player.get("id", "")),
                "position": player.get("position", {}).get("name"),
                "height": player.get("height"),
                "weight": player.get("weight"),
                "age": player.get("age"),
                "draft_year": draft.get("year"),
                "draft_round": draft.get("round"),
                "draft_selection": draft.get("selection"),
                "status": status.get("name"),
            }
            extracted_players[name] = extracted_player
        return [p for p in extracted_players.values()]

    @task
    def load(players: list[dict]):
        clickhouse_client = ClickhouseClient()
        clickhouse_client.write_players(players)

    load.expand(
        players=transform.expand(results=extract.expand(object_path=fetch_players()))
    )


silver_players()
