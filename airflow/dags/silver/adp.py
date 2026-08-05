import logging
from datetime import datetime, date
from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.clickhouse import ClickhouseClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    params={
        "year": Param(2026, type="integer", minimum=2010, maximum=2026),
    },
)
def silver_adp():
    @task
    def fetch_adp(**context):
        year = context["params"]["year"]
        minio_client = MinioClient()
        objects = minio_client.fetch_adp_objects("bronze", year)
        return [o.object_name for o in objects]

    @task
    def elt(object_path: str, **context):
        year = context["params"]["year"]
        print(object_path)
        # extract
        minio_client = MinioClient()
        data = minio_client.read_data("bronze", object_path)

        if data.get("status") != "Success":
            logger.warning("Skipping non-success ADP payload: %s", object_path)
            return

        meta = data.get("meta") or {}
        players = data.get("players") or []

        # transform
        extracted_adp = []
        for player in players:
            extracted_adp.append({
                "source": "ffc",
                "ffc_player_id": int(player.get("player_id")),
                "player_name": player.get("name"),
                "position": player.get("position"),
                "season": year,  # meta has no "year" key - use the DAG param instead
                "scoring_format": meta.get("type"),
                "teams": int(meta.get("teams")),
                "adp": float(player.get("adp")),
                "times_drafted": player.get("times_drafted"),
                "high": player.get("high"),
                "low": player.get("low"),
                "stdev": player.get("stdev"),
                "total_drafts": meta.get("total_drafts"),
                "start_date": date.fromisoformat(meta.get("start_date")),
                "end_date": date.fromisoformat(meta.get("end_date")),
            })

        print(extracted_adp)
        # load
        clickhouse_client = ClickhouseClient()
        clickhouse_client.write_adp(extracted_adp)

    elt.expand(object_path=fetch_adp())


silver_adp()
