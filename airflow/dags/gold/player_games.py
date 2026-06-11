import logging
from datetime import datetime

from airflow.sdk import dag, task
from utils.clickhouse import ClickhouseClient
from utils.queries import INSERT_GOLD

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
)
def gold_player_games():

    @task
    def load():
        clickhouse_client = ClickhouseClient()
        print(INSERT_GOLD)
        values = clickhouse_client.client.command(INSERT_GOLD)
        print(values)

    load()


gold_player_games()
