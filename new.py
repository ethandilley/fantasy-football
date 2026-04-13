import gzip
import json
from dataclasses import asdict, dataclass

import clickhouse_connect
from minio import Minio


@dataclass
class TeamGameStats:
    # identity
    team_id: int
    name: str
    game_id: int
    season: int
    week: int
    home_away: str

    # first downs
    first_downs: int = 0

    # down efficiency
    third_down_conversions: int = 0
    third_down_attempts: int = 0
    fourth_down_conversions: int = 0
    fourth_down_attempts: int = 0

    # overall offense
    total_plays: int = 0
    total_yards: int = 0
    yards_per_play: float = 0.0
    total_drives: int = 0

    # passing
    net_passing_yards: int = 0
    passing_completions: int = 0
    passing_attempts: int = 0
    yards_per_pass: float = 0.0
    interceptions_thrown: int = 0
    sacks: int = 0
    sack_yards_lost: int = 0

    # rushing
    rushing_yards: int = 0
    rushing_attempts: int = 0
    yards_per_rush: float = 0.0

    # red zone
    red_zone_conversions: int = 0
    red_zone_attempts: int = 0

    # turnovers
    turnovers: int = 0
    fumbles_lost: int = 0

    # possession
    possession_time_seconds: int = 0


def parse_fraction(value: str) -> tuple[int, int]:
    """Parse 'made-attempts' or 'made/attempts' strings into (made, attempts)."""
    for sep in ["-", "/"]:
        if sep in value:
            a, b = value.split(sep)
            return int(a), int(b)
    return 0, 0


def get_stat(statistics: list, name: str) -> dict | None:
    """Look up a stat entry by name from the statistics list."""
    for s in statistics:
        if s["name"] == name:
            return s
    return None


year = 2025
week = 1

client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

prefix = f"espn/raw/stats/season={year}/week={week}/"

objects = client.list_objects(
    bucket_name="bronze",
    prefix=prefix,
    recursive=True,
)

object_names = [o.object_name for o in objects]


for object_name in object_names:
    game_id = int(object_name.split("game=")[1].split("/")[0])
    fileobj = client.get_object("bronze", object_name)

    with gzip.GzipFile(fileobj=fileobj) as gz:
        data = json.loads(gz.read().decode("utf-8"))

    teams = []

    for team in data["boxscore"]["teams"]:
        team_id = int(team["team"]["id"])
        home_away = team["homeAway"]
        stats = team["statistics"]

        third_conv, third_att = parse_fraction(
            get_stat(stats, "thirdDownEff")["displayValue"]
        )
        fourth_conv, fourth_att = parse_fraction(
            get_stat(stats, "fourthDownEff")["displayValue"]
        )
        pass_comp, pass_att = parse_fraction(
            get_stat(stats, "completionAttempts")["displayValue"]
        )
        sacks, sack_yards = parse_fraction(
            get_stat(stats, "sacksYardsLost")["displayValue"]
        )
        rz_conv, rz_att = parse_fraction(
            get_stat(stats, "redZoneAttempts")["displayValue"]
        )

        statline = TeamGameStats(
            team_id=team_id,
            name=team["team"]["displayName"],
            game_id=game_id,
            season=year,
            week=week,
            home_away=home_away,
            first_downs=int(get_stat(stats, "firstDowns")["displayValue"]),
            third_down_conversions=third_conv,
            third_down_attempts=third_att,
            fourth_down_conversions=fourth_conv,
            fourth_down_attempts=fourth_att,
            total_plays=int(get_stat(stats, "totalOffensivePlays")["displayValue"]),
            total_yards=int(get_stat(stats, "totalYards")["displayValue"]),
            yards_per_play=float(get_stat(stats, "yardsPerPlay")["displayValue"]),
            total_drives=int(get_stat(stats, "totalDrives")["displayValue"]),
            net_passing_yards=int(get_stat(stats, "netPassingYards")["displayValue"]),
            passing_completions=pass_comp,
            passing_attempts=pass_att,
            yards_per_pass=float(get_stat(stats, "yardsPerPass")["displayValue"]),
            interceptions_thrown=int(get_stat(stats, "interceptions")["displayValue"]),
            sacks=sacks,
            sack_yards_lost=sack_yards,
            rushing_yards=int(get_stat(stats, "rushingYards")["displayValue"]),
            rushing_attempts=int(get_stat(stats, "rushingAttempts")["displayValue"]),
            yards_per_rush=float(
                get_stat(stats, "yardsPerRushAttempt")["displayValue"]
            ),
            red_zone_conversions=rz_conv,
            red_zone_attempts=rz_att,
            turnovers=int(get_stat(stats, "turnovers")["displayValue"]),
            fumbles_lost=int(get_stat(stats, "fumblesLost")["displayValue"]),
            possession_time_seconds=int(get_stat(stats, "possessionTime")["value"]),
        )
        teams.append(statline)

    data = [asdict(p) for p in teams]
    columns = [
        "team_id",
        "name",
        "game_id",
        "season",
        "week",
        "home_away",
        "first_downs",
        "third_down_conversions",
        "third_down_attempts",
        "fourth_down_conversions",
        "fourth_down_attempts",
        "total_plays",
        "total_yards",
        "yards_per_play",
        "total_drives",
        "net_passing_yards",
        "passing_completions",
        "passing_attempts",
        "yards_per_pass",
        "interceptions_thrown",
        "sacks",
        "sack_yards_lost",
        "rushing_yards",
        "rushing_attempts",
        "yards_per_rush",
        "red_zone_conversions",
        "red_zone_attempts",
        "turnovers",
        "fumbles_lost",
        "possession_time_seconds",
    ]
    rows = [[t[col] for col in columns] for t in data]
    print(rows)
