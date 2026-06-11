import logging
from datetime import datetime, date

from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.espn import EspnClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    max_active_tasks=50,
    params={
        "batch_size": Param(25, type="integer", minimum=1, maximum=1000),
    },
)
def bronze_players():

    @task
    def delimit_pages(**context):
        batch_size = context["params"]["batch_size"]
        espn_client = EspnClient()

        player_count = espn_client.get_player_count()
        pages = player_count // batch_size
        parameters = [(i, batch_size) for i in range(pages + 1)]
        return parameters

    @task
    def extract_refs(values: tuple[int, int]):
        page, batch_size = values
        espn_client = EspnClient()
        refs = espn_client.get_players(page=page, limit=batch_size)

        refs_list = []
        for item in refs["items"]:
            refs_list.append(item["$ref"])
        print(refs_list)


        espn_client = EspnClient()

        players = [
            espn_client.get_player_by_ref(ref)
            for ref in refs_list
        ]
        print(players)

        minio_client = MinioClient()
        object_name = minio_client.get_players_object_name(page)
        minio_client.write_data("bronze", object_name, players)

    extract_refs.expand(values=delimit_pages())


bronze_players()
