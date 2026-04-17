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
        values = clickhouse_client.client.command(INSERT_GOLD)
        print(values)

    @task
    def build_features():
        clickhouse_client = ClickhouseClient()
        df = clickhouse_client.client.query_df("select * from gold.playergame final")
        print(df)



    load() >> build_features()


gold_player_games()
