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

    def write_data(self, bucket: str, object_name: str, data: dict | list):
        json_bytes = json.dumps(data).encode("utf-8")

        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(json_bytes)

        buf.seek(0)
        compressed_data = buf.read()

        return self.client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=io.BytesIO(compressed_data),
            length=len(compressed_data),
            content_type="application/gzip",
        )

    def read_data(self, bucket, object_name: str):
        fileobj = self.client.get_object(bucket, object_name)
        with gzip.GzipFile(fileobj=fileobj) as gz:
            raw_bytes = gz.read()
            return json.loads(raw_bytes.decode("utf-8"))

    def fetch_team_objects(self, bucket: str):
        prefix = "espn/raw/teams"
        return self.client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=True,
        )

    def fetch_player_objects(self, bucket: str):
        prefix = "espn/raw/players"
        return self.client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=True,
        )

    def fetch_game_objects(self, bucket: str, year: int, week: int):
        prefix = f"espn/raw/stats/season={year}/week={week}/"
        return self.client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=True,
        )

    def fetch_adp_objects(self, bucket: str, year: int | None = None):
        prefix = "ffc/raw/adp"
        if year is not None:
            prefix += f"/season={year}"
        return self.client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=True,
        )

    def get_events_object_name(self, year: int, week: int):
        return f"espn/raw/events/season={year}/week={week}/data.json.gz"

    def get_stats_object_name(self, year: int, week: int, game_id: str):
        return f"espn/raw/stats/season={year}/week={week}/game={game_id}/data.json.gz"

    def get_players_object_name(self, page: int) -> str:
        return f"espn/raw/players/page={page}/data.json.gz"

    def get_teams_object_name(self, team_id) -> str:
        return f"espn/raw/teams/team_id={team_id}/data.json.gz"

    def get_adp_object_name(self, year: int, scoring_format: str, teams: int) -> str:
        return f"ffc/raw/adp/season={year}/format={scoring_format}/teams={teams}/data.json.gz"

    def get_sportsbook_events_object_name(self, league: str, year: int) -> str:
        return f"sportsbook/{league}/season={year}/events/data.json.gz"

    def get_sportsbook_outcomes_object_name(self, league: str, year: int, market_key: str) -> str:
        return f"sportsbook/{league}/season={year}/outcomes/market_key={market_key}/data.json.gz"
