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
    max_active_tasks=5,
    params={
        "batch_size": Param(100, type="integer", minimum=1, maximum=1000),
    },
)
def players():

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
        return {"page": page, "refs": refs}

    @task
    def load_refs(result: dict):
        print(result)
        page, refs = result["page"], result["refs"]
        minio_client = MinioClient()
        object_name = (
            f"espn/raw/players/date={date.today()}/refs/page={page}/data.json.gz"
        )
        response = minio_client.write_data("bronze", object_name, refs)
        print(response)

        refs_list = []
        for item in result["refs"]["items"]:
            refs_list.append(item["$ref"])
        print(refs_list)
        return {"page": page, "refs": refs_list}

    @task
    def extract_players(result: dict):
        print(result)
        from concurrent.futures import ThreadPoolExecutor, as_completed

        page = result["page"]
        refs = result["refs"]
        espn_client = EspnClient()

        players = []
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {
                pool.submit(espn_client.get_player_by_ref, ref): ref for ref in refs
            }
            for future in as_completed(futures):
                player = future.result()
                if player:
                    players.append(player)

        print(players)

        return {"page": page, "players": players}

    @task
    def load_players(result: dict):
        page, players = result["page"], result["players"]
        minio_client = MinioClient()
        object_name = minio_client.get_players_object_name("players", page)
        minio_client.write_data("bronze", object_name, players)

    @task
    def cleanup():
        print("cleaning")

    (
        load_players.expand(
            result=extract_players.expand(
                result=load_refs.expand(
                    result=extract_refs.expand(values=delimit_pages())
                )
            )
        )
        >> cleanup()
    )


players()
