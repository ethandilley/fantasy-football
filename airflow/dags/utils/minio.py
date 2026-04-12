import gzip
import io
import json
from minio import Minio


class MinioClient:
    def __init__(
        self,
        endpoint="minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    ):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def write_data(self, bucket: str, object_name: str, data: dict):
        json_bytes = json.dumps(data).encode("utf-8")

        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(json_bytes)

        buf.seek(0)
        compressed_data = buf.read()

        self.client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=io.BytesIO(compressed_data),
            length=len(compressed_data),
            content_type="application/gzip",
        )

    def get_events_object_name(self, year: int, week: int):
        return f"espn/raw/events/season={year}/week={week}/data.json.gz"

    def get_stats_object_name(self, year: int, week: int, game_id: str):
        return f"espn/raw/stats/season={year}/week={week}/game={game_id}/data.json.gz"
