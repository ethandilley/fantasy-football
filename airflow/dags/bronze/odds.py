# dags/bronze_sportsbook_odds.py
import logging
from datetime import datetime
from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.sportsbook import SportsbookClient, NFL_COMPETITION_INSTANCE_KEYS

logger = logging.getLogger(__name__)

LEAGUE = "NFL"
BATCH_SIZE = 50


@dag(
    schedule="*/15 * * * *",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    params={
        "year": Param(2026, type="integer", enum=list(NFL_COMPETITION_INSTANCE_KEYS.keys())),
    },
)
def bronze_sportsbook_odds():

    @task
    def get_events(**context):
        year = context["params"]["year"]

        client = SportsbookClient()
        response = client.get_events(year=year)

        minio_client = MinioClient()
        object_name = minio_client.get_sportsbook_events_object_name(LEAGUE, year)
        minio_client.write_data("bronze", object_name, response)

        market_keys = sorted(set(client.get_market_keys(response)))  # dedupe
        return [
            market_keys[i : i + BATCH_SIZE]
            for i in range(0, len(market_keys), BATCH_SIZE)
        ]

    @task
    def get_outcomes(market_key_batch: list[str], **context):
        year = context["params"]["year"]

        client = SportsbookClient()
        minio_client = MinioClient()

        for market_key in market_key_batch:
            response = client.get_market_outcomes_latest(market_key=market_key)
            object_name = minio_client.get_sportsbook_outcomes_object_name(LEAGUE, year, market_key)
            minio_client.write_data("bronze", object_name, response)

    market_key_batches = get_events()
    get_outcomes.expand(market_key_batch=market_key_batches)


bronze_sportsbook_odds()
