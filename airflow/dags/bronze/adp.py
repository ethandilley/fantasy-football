import logging
from datetime import datetime
from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.ffc import FfcClient, FfcApiError, FfcNoDataError

logger = logging.getLogger(__name__)

SCORING_FORMAT = "ppr"
TEAMS = 12


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    params={
        "year": Param(2026, type="integer", minimum=2010, maximum=2026),
    },
)
def bronze_adp_ffc():
    @task
    def extract_and_load_adp(**context):
        year = context["params"]["year"]

        ffc_client = FfcClient()
        try:
            response = ffc_client.get_adp(SCORING_FORMAT, TEAMS, year)
        except FfcNoDataError as e:
            # known gap (e.g. year=2025) - log and skip, don't fail the DAG
            logger.warning(
                "No FFC ADP data: year=%s format=%s teams=%s (%s)",
                year, SCORING_FORMAT, TEAMS, e,
            )
            return
        except FfcApiError as e:
            # transient/network issue - let it fail so Airflow retries
            logger.error(
                "FFC request error: year=%s format=%s teams=%s (%s)",
                year, SCORING_FORMAT, TEAMS, e,
            )
            raise

        minio_client = MinioClient()
        object_name = minio_client.get_adp_object_name(year, SCORING_FORMAT, TEAMS)
        minio_client.write_data("bronze", object_name, response)

    extract_and_load_adp()


bronze_adp_ffc()
