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

    @task
    def build_features():
        clickhouse_client = ClickhouseClient()
        df = clickhouse_client.client.query_df("select * from gold.playergame final")
        print(df)


        # def calculate_fantasy_points(row):
        #     passing_yards = row["passing_yards"]
        #     passing_tds = row["passing_tds"]
        #     interceptions = row["interceptions"]
        #     rushing_yards = row["rushing_yards"]
        #     rushing_tds = row["rushing_tds"]
        #     receptions = row["receptions"]
        #     receiving_yards = row["receiving_yards"]
        #     receiving_tds = row["receiving_tds"]
        #     fumbles_lost = row["fumbles_lost"]
        #
        #     fantasy_points = (
        #         6 * (passing_tds + rushing_tds + receiving_tds)
        #         + 0.1 * (rushing_yards + receiving_yards)
        #         + 0.04 * (passing_yards)
        #         + 1 * receptions
        #         + -2 * (interceptions + fumbles_lost)
        #     )
        #     return fantasy_points
        # df["fantasy_points"] = df.apply(calculate_fantasy_points, axis=1)
        # clickhouse_client.client.insert_dataframe(
        #     'INSERT INTO your_table_name VALUES', 
        #     df, 
        #     settings={'use_numpy': True}
        # )
        #

    load() >> build_features()


gold_player_games()
