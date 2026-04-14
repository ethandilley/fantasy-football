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
    def extract(values: tuple[int, int]):
        page, batch_size = values
        espn_client = EspnClient()
        data = espn_client.get_players(page=page, limit=batch_size)
        return {"page": page, "data": data}

    @task
    def load(result: dict):
        page, data = result["page"], result["data"]
        print(result)
        minio_client = MinioClient()
        object_name = minio_client.get_players_object_name(page)
        minio_client.write_data("bronze", object_name, data)

    @task
    def cleanup():
        print("cleaning")
        # today = str(date.today())
        # prefix_dates = set()
        # minio_client = MinioClient()
        # prefix_objects = minio_client.fetch_player_objects("bronze")
        # prefix_format = "espn/raw/players/date={prefix_date}"
        # for prefix_object in prefix_objects:
        #     prefix_date = prefix_object.object_name.split("date=")[1].split("/")[0]
        #     if prefix_date != today:
        #
        #         prefix_dates.add(prefix_date)
        # minio_client.delete_data("bronze", 
        # # get deletion objects
        # print("cleaned")

    load.expand(result=extract.expand(values=delimit_pages())) >> cleanup()


players()
