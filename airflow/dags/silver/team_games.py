import logging
from datetime import datetime

from airflow.sdk import dag, task, Param
from utils.minio import MinioClient
from utils.espn import EspnClient
from utils.clickhouse import ClickhouseClient

logger = logging.getLogger(__name__)


@dag(
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    params={
        "year": Param(2025, type="integer", minimum=1999, maximum=2025),
        "week": Param(1, type="integer", minimum=1, maximum=17),
    },
)
def populate_team_game_stats():

    @task
    def fetch_games(**context):
        year = context["params"]["year"]
        week = context["params"]["week"]
        print(year)
        print(week)

        minio_client = MinioClient()
        objects = minio_client.fetch_game_objects("bronze", year, week)
        game_paths = [o.object_name for o in objects]
        print(game_paths)

        return game_paths

    @task(multiple_outputs=False)
    def parse_games(game_path: str, **context) -> dict:
        year = context["params"]["year"]
        week = context["params"]["week"]
        print(year)
        print(week)
        print(game_path)

        minio_client = MinioClient()
        game_info = minio_client.read_data("bronze", game_path)
        print(game_info)

        game_id = int(game_path.split("game=")[1].split("/")[0])
        espn_client = EspnClient()
        teams = espn_client.build_teams(game_id, year, week, game_info)
        print(teams)

        return teams

    @task
    def load(teams_game: list[dict]):
        clickhouse_client = ClickhouseClient()
        clickhouse_client.write_team_game_stats(teams_game)

    game_paths = fetch_games()
    teams_games = parse_games.expand(game_path=game_paths)
    load.expand(teams_game=teams_games)


populate_team_game_stats()

{
    "boxscore": {
        "teams": [
            {
                "team": {
                    "id": "1",
                    "uid": "s:20~l:28~t:1",
                    "slug": "atlanta-falcons",
                    "location": "Atlanta",
                    "name": "Falcons",
                    "abbreviation": "ATL",
                    "displayName": "Atlanta Falcons",
                    "shortDisplayName": "Falcons",
                    "color": "000000",
                    "alternateColor": "000000",
                    "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                },
                "statistics": [],
                "displayOrder": 1,
                "homeAway": "away",
            },
            {
                "team": {
                    "id": "6",
                    "uid": "s:20~l:28~t:6",
                    "slug": "dallas-cowboys",
                    "location": "Dallas",
                    "name": "Cowboys",
                    "abbreviation": "DAL",
                    "displayName": "Dallas Cowboys",
                    "shortDisplayName": "Cowboys",
                    "color": "002E4D",
                    "alternateColor": "b0b7bc",
                    "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                },
                "statistics": [],
                "displayOrder": 2,
                "homeAway": "home",
            },
        ],
        "players": [
            {
                "team": {
                    "id": "1",
                    "uid": "s:20~l:28~t:1",
                    "slug": "atlanta-falcons",
                    "location": "Atlanta",
                    "name": "Falcons",
                    "abbreviation": "ATL",
                    "displayName": "Atlanta Falcons",
                    "shortDisplayName": "Falcons",
                    "color": "000000",
                    "alternateColor": "000000",
                    "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                },
                "statistics": [
                    {
                        "name": "passing",
                        "keys": [
                            "completions/passingAttempts",
                            "passingYards",
                            "yardsPerPassAttempt",
                            "passingTouchdowns",
                            "interceptions",
                            "sacks-sackYardsLost",
                            "adjQBR",
                            "QBRating",
                        ],
                        "text": "Atlanta Passing",
                        "labels": ["C/ATT", "YDS", "AVG", "TD", "INT", "SACKS", "RTG"],
                        "descriptions": [
                            "Completions/Attempts",
                            "Yards",
                            "Yards Per Pass Attempt",
                            "Touchdowns",
                            "Interceptions",
                            "Sacks",
                            "Passer Rating",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "rushing",
                        "keys": [
                            "rushingAttempts",
                            "rushingYards",
                            "yardsPerRushAttempt",
                            "rushingTouchdowns",
                            "longRushing",
                        ],
                        "text": "Atlanta Rushing",
                        "labels": ["CAR", "YDS", "AVG", "TD", "LONG"],
                        "descriptions": [
                            "Rushing Attempts",
                            "Yards",
                            "Yards Per Rushing Attempt",
                            "Touchdowns",
                            "Longest Run",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "receiving",
                        "keys": [
                            "receptions",
                            "receivingYards",
                            "yardsPerReception",
                            "receivingTouchdowns",
                            "longReception",
                            "receivingTargets",
                        ],
                        "text": "Atlanta Receiving",
                        "labels": ["REC", "YDS", "AVG", "TD", "LONG", "TGTS"],
                        "descriptions": [
                            "Receptions",
                            "Yards",
                            "Yards Per Reception",
                            "Touchdowns",
                            "Longest Reception",
                            "Receiving Targets",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "fumbles",
                        "keys": ["fumbles", "fumblesLost", "fumblesRecovered"],
                        "text": "Atlanta Fumbles",
                        "labels": ["FUM", "LOST", "REC"],
                        "descriptions": [
                            "Fumbles",
                            "Fumbles Lost",
                            "Fumbles Recovered",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "defensive",
                        "keys": [
                            "totalTackles",
                            "soloTackles",
                            "sacks",
                            "tacklesForLoss",
                            "passesDefended",
                            "QBHits",
                            "defensiveTouchdowns",
                        ],
                        "text": "Atlanta Defense",
                        "labels": ["TOT", "SOLO", "SACKS", "TFL", "PD", "QB HTS", "TD"],
                        "descriptions": [
                            "Tackles",
                            "Solo Tackles",
                            "Sacks",
                            "Tackles For Loss",
                            "Passes Defended",
                            "Quarterback Hits",
                            "Touchdowns",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "interceptions",
                        "keys": [
                            "interceptions",
                            "interceptionYards",
                            "interceptionTouchdowns",
                        ],
                        "text": "Atlanta Interceptions",
                        "labels": ["INT", "YDS", "TD"],
                        "descriptions": ["Interceptions", "Yards", "Touchdowns"],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "kickReturns",
                        "keys": [
                            "kickReturns",
                            "kickReturnYards",
                            "yardsPerKickReturn",
                            "longKickReturn",
                            "kickReturnTouchdowns",
                        ],
                        "text": "Atlanta Kick Returns",
                        "labels": ["NO", "YDS", "AVG", "LONG", "TD"],
                        "descriptions": [
                            "Kick Returns",
                            "Yards",
                            "Yards Per Kick Return",
                            "Longest Kick Return",
                            "Touchdowns",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "puntReturns",
                        "keys": [
                            "puntReturns",
                            "puntReturnYards",
                            "yardsPerPuntReturn",
                            "longPuntReturn",
                            "puntReturnTouchdowns",
                        ],
                        "text": "Atlanta Punt Returns",
                        "labels": ["NO", "YDS", "AVG", "LONG", "TD"],
                        "descriptions": [
                            "Punt Returns",
                            "Yards",
                            "Yards Per Punt Return",
                            "Longest Punt Return",
                            "Touchdowns",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "kicking",
                        "keys": [
                            "fieldGoalsMade/fieldGoalAttempts",
                            "fieldGoalPct",
                            "longFieldGoalMade",
                            "extraPointsMade/extraPointAttempts",
                            "totalKickingPoints",
                        ],
                        "text": "Atlanta Kicking",
                        "labels": ["FG", "PCT", "LONG", "XP", "PTS"],
                        "descriptions": [
                            "Field Goals Made/Attempts",
                            "Field Goal Percentage",
                            "Longest Field Goal Made",
                            "Extra Points Made/Attempts",
                            "Kicking Points",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "punting",
                        "keys": [
                            "punts",
                            "puntYards",
                            "grossAvgPuntYards",
                            "touchbacks",
                            "puntsInside20",
                            "longPunt",
                        ],
                        "text": "Atlanta Punting",
                        "labels": ["NO", "YDS", "AVG", "TB", "In 20", "LONG"],
                        "descriptions": [
                            "Punts",
                            "Yards",
                            "Average Punt Yards",
                            "Touchbacks",
                            "Punts Inside 20",
                            "Longest Punt",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                ],
                "displayOrder": 1,
            },
            {
                "team": {
                    "id": "6",
                    "uid": "s:20~l:28~t:6",
                    "slug": "dallas-cowboys",
                    "location": "Dallas",
                    "name": "Cowboys",
                    "abbreviation": "DAL",
                    "displayName": "Dallas Cowboys",
                    "shortDisplayName": "Cowboys",
                    "color": "002E4D",
                    "alternateColor": "b0b7bc",
                    "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                },
                "statistics": [
                    {
                        "name": "passing",
                        "keys": [
                            "completions/passingAttempts",
                            "passingYards",
                            "yardsPerPassAttempt",
                            "passingTouchdowns",
                            "interceptions",
                            "sacks-sackYardsLost",
                            "adjQBR",
                            "QBRating",
                        ],
                        "text": "Dallas Passing",
                        "labels": ["C/ATT", "YDS", "AVG", "TD", "INT", "SACKS", "RTG"],
                        "descriptions": [
                            "Completions/Attempts",
                            "Yards",
                            "Yards Per Pass Attempt",
                            "Touchdowns",
                            "Interceptions",
                            "Sacks",
                            "Passer Rating",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "rushing",
                        "keys": [
                            "rushingAttempts",
                            "rushingYards",
                            "yardsPerRushAttempt",
                            "rushingTouchdowns",
                            "longRushing",
                        ],
                        "text": "Dallas Rushing",
                        "labels": ["CAR", "YDS", "AVG", "TD", "LONG"],
                        "descriptions": [
                            "Rushing Attempts",
                            "Yards",
                            "Yards Per Rushing Attempt",
                            "Touchdowns",
                            "Longest Run",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "receiving",
                        "keys": [
                            "receptions",
                            "receivingYards",
                            "yardsPerReception",
                            "receivingTouchdowns",
                            "longReception",
                            "receivingTargets",
                        ],
                        "text": "Dallas Receiving",
                        "labels": ["REC", "YDS", "AVG", "TD", "LONG", "TGTS"],
                        "descriptions": [
                            "Receptions",
                            "Yards",
                            "Yards Per Reception",
                            "Touchdowns",
                            "Longest Reception",
                            "Receiving Targets",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "fumbles",
                        "keys": ["fumbles", "fumblesLost", "fumblesRecovered"],
                        "text": "Dallas Fumbles",
                        "labels": ["FUM", "LOST", "REC"],
                        "descriptions": [
                            "Fumbles",
                            "Fumbles Lost",
                            "Fumbles Recovered",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "defensive",
                        "keys": [
                            "totalTackles",
                            "soloTackles",
                            "sacks",
                            "tacklesForLoss",
                            "passesDefended",
                            "QBHits",
                            "defensiveTouchdowns",
                        ],
                        "text": "Dallas Defense",
                        "labels": ["TOT", "SOLO", "SACKS", "TFL", "PD", "QB HTS", "TD"],
                        "descriptions": [
                            "Tackles",
                            "Solo Tackles",
                            "Sacks",
                            "Tackles For Loss",
                            "Passes Defended",
                            "Quarterback Hits",
                            "Touchdowns",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "interceptions",
                        "keys": [
                            "interceptions",
                            "interceptionYards",
                            "interceptionTouchdowns",
                        ],
                        "text": "Dallas Interceptions",
                        "labels": ["INT", "YDS", "TD"],
                        "descriptions": ["Interceptions", "Yards", "Touchdowns"],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "kickReturns",
                        "keys": [
                            "kickReturns",
                            "kickReturnYards",
                            "yardsPerKickReturn",
                            "longKickReturn",
                            "kickReturnTouchdowns",
                        ],
                        "text": "Dallas Kick Returns",
                        "labels": ["NO", "YDS", "AVG", "LONG", "TD"],
                        "descriptions": [
                            "Kick Returns",
                            "Yards",
                            "Yards Per Kick Return",
                            "Longest Kick Return",
                            "Touchdowns",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "puntReturns",
                        "keys": [
                            "puntReturns",
                            "puntReturnYards",
                            "yardsPerPuntReturn",
                            "longPuntReturn",
                            "puntReturnTouchdowns",
                        ],
                        "text": "Dallas Punt Returns",
                        "labels": ["NO", "YDS", "AVG", "LONG", "TD"],
                        "descriptions": [
                            "Punt Returns",
                            "Yards",
                            "Yards Per Punt Return",
                            "Longest Punt Return",
                            "Touchdowns",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "kicking",
                        "keys": [
                            "fieldGoalsMade/fieldGoalAttempts",
                            "fieldGoalPct",
                            "longFieldGoalMade",
                            "extraPointsMade/extraPointAttempts",
                            "totalKickingPoints",
                        ],
                        "text": "Dallas Kicking",
                        "labels": ["FG", "PCT", "LONG", "XP", "PTS"],
                        "descriptions": [
                            "Field Goals Made/Attempts",
                            "Field Goal Percentage",
                            "Longest Field Goal Made",
                            "Extra Points Made/Attempts",
                            "Kicking Points",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                    {
                        "name": "punting",
                        "keys": [
                            "punts",
                            "puntYards",
                            "grossAvgPuntYards",
                            "touchbacks",
                            "puntsInside20",
                            "longPunt",
                        ],
                        "text": "Dallas Punting",
                        "labels": ["NO", "YDS", "AVG", "TB", "In 20", "LONG"],
                        "descriptions": [
                            "Punts",
                            "Yards",
                            "Average Punt Yards",
                            "Touchbacks",
                            "Punts Inside 20",
                            "Longest Punt",
                        ],
                        "athletes": [],
                        "totals": [],
                    },
                ],
                "displayOrder": 2,
            },
        ],
    },
    "format": {
        "regulation": {
            "periods": 4,
            "displayName": "Quarter",
            "slug": "quarter",
            "clock": 900.0,
        },
        "overtime": {
            "periods": 1,
            "displayName": "sudden-death",
            "slug": "sudden-death",
            "clock": 600.0,
        },
        "suddenDeath": {"periods": 1, "clock": 600.0},
    },
    "gameInfo": {
        "venue": {
            "id": "3954",
            "guid": "8d72bbbc-7fc2-3e45-8e96-667471162137",
            "fullName": "Texas Stadium",
            "address": {"city": "Irving", "state": "TX", "country": "USA"},
            "grass": False,
            "images": [],
        },
        "attendance": 63663,
        "officials": [
            {
                "fullName": "Thomas White",
                "displayName": "Thomas White",
                "position": {"name": "Referee", "displayName": "Referee", "id": "40"},
                "order": 1,
            }
        ],
    },
    "leaders": [
        {
            "team": {
                "id": "6",
                "uid": "s:20~l:28~t:6",
                "displayName": "Dallas Cowboys",
                "abbreviation": "DAL",
                "links": [
                    {
                        "href": "https://www.espn.com/nfl/team/_/name/dal/dallas-cowboys",
                        "text": "Clubhouse",
                    },
                    {
                        "href": "https://www.espn.com/nfl/team/schedule/_/name/dal",
                        "text": "Schedule",
                    },
                ],
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                "logos": [
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "default"],
                        "lastUpdated": "2024-06-25T18:47Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "dark"],
                        "lastUpdated": "2024-06-25T18:59Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard"],
                        "lastUpdated": "2024-06-25T18:48Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard", "dark"],
                        "lastUpdated": "2024-06-25T18:59Z",
                    },
                ],
            },
            "leaders": [
                {"name": "passingYards", "displayName": "Passing Yards"},
                {"name": "rushingYards", "displayName": "Rushing Yards"},
                {"name": "receivingYards", "displayName": "Receiving Yards"},
                {"name": "sacks", "displayName": "Sacks"},
                {"name": "totalTackles", "displayName": "Tackles"},
            ],
        },
        {
            "team": {
                "id": "1",
                "uid": "s:20~l:28~t:1",
                "displayName": "Atlanta Falcons",
                "abbreviation": "ATL",
                "links": [
                    {
                        "href": "https://www.espn.com/nfl/team/_/name/atl/atlanta-falcons",
                        "text": "Clubhouse",
                    },
                    {
                        "href": "https://www.espn.com/nfl/team/schedule/_/name/atl",
                        "text": "Schedule",
                    },
                ],
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                "logos": [
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "default"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "dark"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard", "dark"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                ],
            },
            "leaders": [
                {"name": "passingYards", "displayName": "Passing Yards"},
                {"name": "rushingYards", "displayName": "Rushing Yards"},
                {"name": "receivingYards", "displayName": "Receiving Yards"},
                {"name": "sacks", "displayName": "Sacks"},
                {"name": "totalTackles", "displayName": "Tackles"},
            ],
        },
    ],
    "injuries": [
        {
            "team": {
                "id": "6",
                "uid": "s:20~l:28~t:6",
                "displayName": "Dallas Cowboys",
                "abbreviation": "DAL",
                "links": [
                    {
                        "href": "https://www.espn.com/nfl/team/_/name/dal/dallas-cowboys",
                        "text": "Clubhouse",
                    },
                    {
                        "href": "https://www.espn.com/nfl/team/schedule/_/name/dal",
                        "text": "Schedule",
                    },
                ],
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                "logos": [
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "default"],
                        "lastUpdated": "2024-06-25T18:47Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "dark"],
                        "lastUpdated": "2024-06-25T18:59Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard"],
                        "lastUpdated": "2024-06-25T18:48Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard", "dark"],
                        "lastUpdated": "2024-06-25T18:59Z",
                    },
                ],
            },
            "injuries": [
                {
                    "status": "Questionable",
                    "date": "2026-04-11T15:49Z",
                    "athlete": {
                        "id": "4241921",
                        "uid": "s:20~l:28~a:4241921",
                        "guid": "443970ca-f31c-33df-4115-dc7954c033ef",
                        "lastName": "Bell",
                        "fullName": "Markquese Bell",
                        "displayName": "Markquese Bell",
                        "shortName": "M. Bell",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4241921/markquese-bell",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4241921.png",
                            "alt": "Markquese Bell",
                        },
                        "jersey": "14",
                        "position": {
                            "name": "Safety",
                            "displayName": "Safety",
                            "abbreviation": "S",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4241921?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Concussion",
                        "location": "Head",
                        "detail": "Concussion",
                        "side": "Not Specified",
                        "returnDate": "2026-05-01",
                    },
                },
                {
                    "status": "Questionable",
                    "date": "2026-03-02T17:13Z",
                    "athlete": {
                        "id": "4683848",
                        "uid": "s:20~l:28~a:4683848",
                        "guid": "28500588-8fa9-368f-999c-d3cb4f4dbf1f",
                        "lastName": "Ezeiruaku",
                        "fullName": "Donovan Ezeiruaku",
                        "displayName": "Donovan Ezeiruaku",
                        "shortName": "D. Ezeiruaku",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4683848/donovan-ezeiruaku",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4683848.png",
                            "alt": "Donovan Ezeiruaku",
                        },
                        "jersey": "41",
                        "position": {
                            "name": "Defensive End",
                            "displayName": "Defensive End",
                            "abbreviation": "DE",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4683848?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Hip",
                        "location": "Leg",
                        "detail": "Surgery",
                        "side": "Not Specified",
                        "returnDate": "2026-05-01",
                    },
                },
                {
                    "status": "Questionable",
                    "date": "2026-02-25T16:50Z",
                    "athlete": {
                        "id": "4568652",
                        "uid": "s:20~l:28~a:4568652",
                        "guid": "84db0c55-2277-2d48-f164-595a103b4acf",
                        "lastName": "Smith",
                        "fullName": "Tyler Smith",
                        "displayName": "Tyler Smith",
                        "shortName": "T. Smith",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4568652/tyler-smith",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4568652.png",
                            "alt": "Tyler Smith",
                        },
                        "jersey": "73",
                        "position": {
                            "name": "Guard",
                            "displayName": "Guard",
                            "abbreviation": "G",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4568652?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Knee",
                        "location": "Leg",
                        "detail": "Not Specified",
                        "side": "Right",
                        "returnDate": "2026-05-01",
                    },
                },
                {
                    "status": "Questionable",
                    "date": "2026-02-21T21:44Z",
                    "athlete": {
                        "id": "4361579",
                        "uid": "s:20~l:28~a:4361579",
                        "guid": "0e04df01-7c44-1b1e-01a3-f73ab6f4eb61",
                        "lastName": "Williams",
                        "fullName": "Javonte Williams",
                        "displayName": "Javonte Williams",
                        "shortName": "J. Williams",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4361579/javonte-williams",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4361579.png",
                            "alt": "Javonte Williams",
                        },
                        "jersey": "33",
                        "position": {
                            "name": "Running Back",
                            "displayName": "Running Back",
                            "abbreviation": "RB",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4361579?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Shoulder",
                        "location": "Arm",
                        "detail": "Not Specified",
                        "side": "Not Specified",
                        "returnDate": "2026-05-01",
                    },
                },
                {
                    "status": "Questionable",
                    "date": "2026-02-11T23:55Z",
                    "athlete": {
                        "id": "4427140",
                        "uid": "s:20~l:28~a:4427140",
                        "guid": "c4e9168a-92c2-3e5b-3423-f6e438162b91",
                        "lastName": "Keegan",
                        "fullName": "Trevor Keegan",
                        "displayName": "Trevor Keegan",
                        "shortName": "T. Keegan",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4427140/trevor-keegan",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4427140.png",
                            "alt": "Trevor Keegan",
                        },
                        "jersey": "76",
                        "position": {
                            "name": "Guard",
                            "displayName": "Guard",
                            "abbreviation": "G",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4427140?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Neck",
                        "location": "Head",
                        "detail": "Not Specified",
                        "side": "Not Specified",
                        "returnDate": "2026-05-01",
                    },
                },
            ],
        },
        {
            "team": {
                "id": "1",
                "uid": "s:20~l:28~t:1",
                "displayName": "Atlanta Falcons",
                "abbreviation": "ATL",
                "links": [
                    {
                        "href": "https://www.espn.com/nfl/team/_/name/atl/atlanta-falcons",
                        "text": "Clubhouse",
                    },
                    {
                        "href": "https://www.espn.com/nfl/team/schedule/_/name/atl",
                        "text": "Schedule",
                    },
                ],
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                "logos": [
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "default"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "dark"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard", "dark"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                ],
            },
            "injuries": [
                {
                    "status": "Questionable",
                    "date": "2026-03-13T19:29Z",
                    "athlete": {
                        "id": "4360423",
                        "uid": "s:20~l:28~a:4360423",
                        "guid": "28022fa1-9050-eee1-5160-c77a6a379ec2",
                        "lastName": "Penix Jr.",
                        "fullName": "Michael Penix Jr.",
                        "displayName": "Michael Penix Jr.",
                        "shortName": "M. Penix Jr.",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4360423/michael-penix-jr",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4360423.png",
                            "alt": "Michael Penix Jr.",
                        },
                        "jersey": "9",
                        "position": {
                            "name": "Quarterback",
                            "displayName": "Quarterback",
                            "abbreviation": "QB",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4360423?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Knee - ACL",
                        "location": "Leg",
                        "detail": "Surgery",
                        "side": "Left",
                        "returnDate": "2026-08-01",
                    },
                },
                {
                    "status": "Questionable",
                    "date": "2026-03-11T21:38Z",
                    "athlete": {
                        "id": "2973637",
                        "uid": "s:20~l:28~a:2973637",
                        "guid": "14ae0407-4094-3f00-dbb6-527477d0e978",
                        "lastName": "Levin",
                        "fullName": "Corey Levin",
                        "displayName": "Corey Levin",
                        "shortName": "C. Levin",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/2973637/corey-levin",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/2973637.png",
                            "alt": "Corey Levin",
                        },
                        "jersey": "62",
                        "position": {
                            "name": "Guard",
                            "displayName": "Guard",
                            "abbreviation": "G",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/533059?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Biceps",
                        "location": "Arm",
                        "detail": "Not Specified",
                        "side": "Not Specified",
                        "returnDate": "2026-05-01",
                    },
                },
                {
                    "status": "Questionable",
                    "date": "2026-03-11T19:52Z",
                    "athlete": {
                        "id": "4379409",
                        "uid": "s:20~l:28~a:4379409",
                        "guid": "79d7db8e-68aa-75ce-a60b-84382675fce6",
                        "lastName": "Ojulari",
                        "fullName": "Azeez Ojulari",
                        "displayName": "Azeez Ojulari",
                        "shortName": "A. Ojulari",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4379409/azeez-ojulari",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4379409.png",
                            "alt": "Azeez Ojulari",
                        },
                        "position": {
                            "name": "Linebacker",
                            "displayName": "Linebacker",
                            "abbreviation": "LB",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4379409?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Hamstring",
                        "location": "Leg",
                        "detail": "Not Specified",
                        "side": "Not Specified",
                        "returnDate": "2026-05-01",
                    },
                },
                {
                    "status": "Questionable",
                    "date": "2026-02-11T20:31Z",
                    "athlete": {
                        "id": "4428713",
                        "uid": "s:20~l:28~a:4428713",
                        "guid": "f980ad68-3aa0-b32f-641b-b478834c7d5b",
                        "lastName": "Trice",
                        "fullName": "Bralen Trice",
                        "displayName": "Bralen Trice",
                        "shortName": "B. Trice",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4428713/bralen-trice",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4428713.png",
                            "alt": "Bralen Trice",
                        },
                        "jersey": "48",
                        "position": {
                            "name": "Linebacker",
                            "displayName": "Linebacker",
                            "abbreviation": "LB",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4428713?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Knee",
                        "location": "Leg",
                        "detail": "Not Specified",
                        "side": "Not Specified",
                        "returnDate": "2026-05-01",
                    },
                },
                {
                    "status": "Questionable",
                    "date": "2026-02-11T20:31Z",
                    "athlete": {
                        "id": "4684636",
                        "uid": "s:20~l:28~a:4684636",
                        "guid": "d958083f-2e81-3656-b542-b6350425e3cc",
                        "lastName": "Verdon",
                        "fullName": "Malik Verdon",
                        "displayName": "Malik Verdon",
                        "shortName": "M. Verdon",
                        "links": [
                            {
                                "rel": ["playercard", "desktop", "athlete"],
                                "href": "https://www.espn.com/nfl/player/_/id/4684636/malik-verdon",
                                "text": "Player Card",
                            }
                        ],
                        "headshot": {
                            "href": "https://a.espncdn.com/i/headshots/nfl/players/full/4684636.png",
                            "alt": "Malik Verdon",
                        },
                        "jersey": "43",
                        "position": {
                            "name": "Safety",
                            "displayName": "Safety",
                            "abbreviation": "S",
                        },
                        "collegeAthlete": {
                            "$ref": "http://sports.core.api.espn.pvt/v2/sports/football/leagues/college-football/athletes/4684636?lang=en&region=us"
                        },
                        "status": {
                            "id": "1",
                            "name": "Active",
                            "type": "active",
                            "abbreviation": "Active",
                        },
                    },
                    "type": {
                        "id": "2",
                        "name": "INJURY_STATUS_QUESTIONABLE",
                        "description": "questionable",
                        "abbreviation": "Q",
                    },
                    "details": {
                        "fantasyStatus": {
                            "description": "QUESTIONABLE",
                            "abbreviation": "QUESTIONABLE",
                            "displayDescription": "Questionable",
                        },
                        "type": "Shoulder",
                        "location": "Arm",
                        "detail": "Not Specified",
                        "side": "Not Specified",
                        "returnDate": "2026-05-01",
                    },
                },
            ],
        },
    ],
    "broadcasts": [],
    "pickcenter": [],
    "odds": [],
    "againstTheSpread": [
        {
            "team": {
                "id": "1",
                "uid": "s:20~l:28~t:1",
                "displayName": "Atlanta Falcons",
                "abbreviation": "ATL",
                "links": [
                    {
                        "href": "https://www.espn.com/nfl/team/_/name/atl/atlanta-falcons",
                        "text": "Clubhouse",
                    },
                    {
                        "href": "https://www.espn.com/nfl/team/schedule/_/name/atl",
                        "text": "Schedule",
                    },
                ],
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                "logos": [
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "default"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "dark"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/atl.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard", "dark"],
                        "lastUpdated": "2024-06-25T18:44Z",
                    },
                ],
            },
            "records": [],
        },
        {
            "team": {
                "id": "6",
                "uid": "s:20~l:28~t:6",
                "displayName": "Dallas Cowboys",
                "abbreviation": "DAL",
                "links": [
                    {
                        "href": "https://www.espn.com/nfl/team/_/name/dal/dallas-cowboys",
                        "text": "Clubhouse",
                    },
                    {
                        "href": "https://www.espn.com/nfl/team/schedule/_/name/dal",
                        "text": "Schedule",
                    },
                ],
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                "logos": [
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "default"],
                        "lastUpdated": "2024-06-25T18:47Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "dark"],
                        "lastUpdated": "2024-06-25T18:59Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard"],
                        "lastUpdated": "2024-06-25T18:48Z",
                    },
                    {
                        "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/dal.png",
                        "width": 500,
                        "height": 500,
                        "alt": "",
                        "rel": ["full", "scoreboard", "dark"],
                        "lastUpdated": "2024-06-25T18:59Z",
                    },
                ],
            },
            "records": [],
        },
    ],
    "winprobability": [],
    "header": {
        "id": "190920006",
        "uid": "s:20~l:28~e:190920006",
        "season": {"year": 1999, "current": False, "type": 2},
        "timeValid": True,
        "competitions": [
            {
                "id": "190920006",
                "uid": "s:20~l:28~e:190920006~c:190920006",
                "date": "1999-09-20T16:00Z",
                "neutralSite": False,
                "conferenceCompetition": False,
                "boxscoreAvailable": True,
                "commentaryAvailable": False,
                "liveAvailable": False,
                "onWatchESPN": False,
                "recent": False,
                "wallclockAvailable": False,
                "boxscoreSource": "full",
                "playByPlaySource": "full",
                "competitors": [
                    {
                        "id": "6",
                        "uid": "s:20~l:28~t:6",
                        "order": 0,
                        "homeAway": "home",
                        "winner": False,
                        "team": {
                            "id": "6",
                            "guid": "b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234",
                            "uid": "s:20~l:28~t:6",
                            "location": "Dallas",
                            "name": "Cowboys",
                            "nickname": "Cowboys",
                            "abbreviation": "DAL",
                            "displayName": "Dallas Cowboys",
                            "color": "002E4D",
                            "alternateColor": "b0b7bc",
                            "logos": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:47Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/dal.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "dark"],
                                    "lastUpdated": "2024-06-25T18:59Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/dal.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard"],
                                    "lastUpdated": "2024-06-25T18:48Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/dal.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:59Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/grayscale.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "grayscale"],
                                    "lastUpdated": "2026-03-31T12:54Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/primary_logo_on_white_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_on_white_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/primary_logo_on_black_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_on_black_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/primary_logo_on_primary_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_on_primary_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/primary_logo_on_secondary_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_on_secondary_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/primary_logo_black.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_black"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/primary_logo_white.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_white"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/secondary_logo_on_white_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_on_white_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/secondary_logo_on_black_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_on_black_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/secondary_logo_on_primary_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_on_primary_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/secondary_logo_on_secondary_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": [
                                        "full",
                                        "secondary_logo_on_secondary_color",
                                    ],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/secondary_logo_black.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_black"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/b0fc8fb7-9dbe-e574-9008-6f0ee7c6b234/logos/secondary_logo_white.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_white"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                            ],
                            "links": [
                                {
                                    "rel": ["clubhouse", "desktop", "team"],
                                    "href": "https://www.espn.com/nfl/team/_/name/dal/dallas-cowboys",
                                    "text": "Clubhouse",
                                }
                            ],
                        },
                        "score": "0",
                        "record": [
                            {"type": "total", "summary": "2-0", "displayValue": "2-0"},
                            {"type": "home", "summary": "1-0", "displayValue": "1-0"},
                        ],
                        "possession": False,
                    },
                    {
                        "id": "1",
                        "uid": "s:20~l:28~t:1",
                        "order": 1,
                        "homeAway": "away",
                        "winner": False,
                        "team": {
                            "id": "1",
                            "guid": "49fd392a-86fe-4df3-1b77-9bbfa18b2ad5",
                            "uid": "s:20~l:28~t:1",
                            "location": "Atlanta",
                            "name": "Falcons",
                            "nickname": "Falcons",
                            "abbreviation": "ATL",
                            "displayName": "Atlanta Falcons",
                            "color": "000000",
                            "alternateColor": "000000",
                            "logos": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:44Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/atl.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "dark"],
                                    "lastUpdated": "2024-06-25T18:44Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/atl.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard"],
                                    "lastUpdated": "2024-06-25T18:44Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/atl.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:44Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/grayscale.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "grayscale"],
                                    "lastUpdated": "2026-03-31T12:54Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/primary_logo_on_white_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_on_white_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/primary_logo_on_black_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_on_black_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/primary_logo_on_primary_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_on_primary_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/primary_logo_on_secondary_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_on_secondary_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/primary_logo_black.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_black"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/primary_logo_white.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "primary_logo_white"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/secondary_logo_on_white_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_on_white_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/secondary_logo_on_black_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_on_black_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/secondary_logo_on_primary_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_on_primary_color"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/secondary_logo_on_secondary_color.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": [
                                        "full",
                                        "secondary_logo_on_secondary_color",
                                    ],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/secondary_logo_black.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_black"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/guid/49fd392a-86fe-4df3-1b77-9bbfa18b2ad5/logos/secondary_logo_white.png",
                                    "width": 4096,
                                    "height": 4096,
                                    "alt": "",
                                    "rel": ["full", "secondary_logo_white"],
                                    "lastUpdated": "2026-02-13T03:12Z",
                                },
                            ],
                            "links": [
                                {
                                    "rel": ["clubhouse", "desktop", "team"],
                                    "href": "https://www.espn.com/nfl/team/_/name/atl/atlanta-falcons",
                                    "text": "Clubhouse",
                                }
                            ],
                        },
                        "score": "0",
                        "record": [
                            {"type": "total", "summary": "0-2", "displayValue": "0-2"},
                            {"type": "road", "summary": "0-1", "displayValue": "0-1"},
                        ],
                        "possession": False,
                    },
                ],
                "status": {
                    "type": {
                        "id": "3",
                        "name": "STATUS_FINAL",
                        "state": "post",
                        "completed": True,
                        "description": "Final",
                        "detail": "Final",
                        "shortDetail": "Final",
                    },
                    "isTBDFlex": False,
                },
                "broadcasts": [],
                "boxscoreMinutes": True,
            }
        ],
        "links": [
            {
                "rel": ["summary", "desktop", "event"],
                "href": "https://www.espn.com/nfl/game/_/gameId/190920006/falcons-cowboys",
                "text": "Gamecast",
                "shortText": "Summary",
                "isExternal": False,
                "isPremium": False,
            },
            {
                "rel": ["boxscore", "desktop", "event"],
                "href": "https://www.espn.com/nfl/boxscore/_/gameId/190920006",
                "text": "Box Score",
                "shortText": "Box Score",
                "isExternal": False,
                "isPremium": False,
            },
            {
                "rel": ["pbp", "desktop", "event"],
                "href": "https://www.espn.com/nfl/playbyplay/_/gameId/190920006",
                "text": "Play-by-Play",
                "shortText": "Play-by-Play",
                "isExternal": False,
                "isPremium": False,
            },
            {
                "rel": ["teamstats", "desktop", "event"],
                "href": "https://www.espn.com/nfl/matchup?gameId=190920006",
                "text": "Team Stats",
                "shortText": "Team Stats",
                "isExternal": False,
                "isPremium": False,
            },
            {
                "rel": ["fantasy", "desktop", "event"],
                "href": "https://fantasy.espn.com/football/welcome?addata=nfl_gamecast_ffl1999",
                "text": "Play Fantasy Football",
                "shortText": "Play Fantasy Football",
                "isExternal": False,
                "isPremium": False,
            },
        ],
        "week": 2,
        "league": {
            "id": "28",
            "uid": "s:20~l:28",
            "name": "National Football League",
            "abbreviation": "NFL",
            "slug": "nfl",
            "isTournament": False,
            "links": [
                {
                    "rel": ["index", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/",
                    "text": "Index",
                },
                {
                    "rel": ["index", "sportscenter", "app", "league"],
                    "href": "sportscenter://x-callback-url/showClubhouse?uid=s:20~l:28",
                    "text": "Index",
                },
                {
                    "rel": ["schedule", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/schedule",
                    "text": "Schedule",
                },
                {
                    "rel": ["schedule", "sportscenter", "app", "league"],
                    "href": "sportscenter://x-callback-url/showClubhouse?uid=s:20~l:28&section=scores",
                    "text": "Schedule",
                },
                {
                    "rel": ["standings", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/standings",
                    "text": "Standings",
                },
                {
                    "rel": ["standings", "sportscenter", "app", "league"],
                    "href": "sportscenter://x-callback-url/showClubhouse?uid=s:20~l:28&section=standings",
                    "text": "Standings",
                },
                {
                    "rel": ["rankings", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/powerrankings",
                    "text": "Power Rankings",
                },
                {
                    "rel": ["scores", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/scoreboard",
                    "text": "Scores",
                },
                {
                    "rel": ["scores", "sportscenter", "app", "league"],
                    "href": "sportscenter://x-callback-url/showClubhouse?uid=s:20~l:28&section=scores",
                    "text": "Scores",
                },
                {
                    "rel": ["stats", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/stats",
                    "text": "Stats",
                },
                {
                    "rel": ["teams", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/teams",
                    "text": "Teams",
                },
                {
                    "rel": ["athletes", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/players",
                    "text": "Players",
                },
                {
                    "rel": ["injuries", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/injuries",
                    "text": "Injuries",
                },
                {
                    "rel": ["odds", "desktop", "league"],
                    "href": "https://www.espn.com/nfl/odds",
                    "text": "Odds",
                },
                {
                    "rel": ["odds", "sportscenter", "app", "league"],
                    "href": "sportscenter://x-callback-url/showClubhouse?uid=s:20~l:28&section=odds",
                    "text": "Odds",
                },
                {
                    "rel": ["freeagency", "desktop", "league"],
                    "href": "https://insider.espn.com/nfl/freeagency/",
                    "text": "Freeagency",
                },
            ],
            "logos": [
                {
                    "href": "https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png",
                    "rel": ["full", "default"],
                },
                {
                    "href": "https://a.espncdn.com/i/teamlogos/leagues/500-dark/nfl.png",
                    "rel": ["full", "dark"],
                },
            ],
        },
    },
    "news": {
        "header": "NFL News",
        "link": {
            "language": "en",
            "rel": ["index", "desktop", "league"],
            "href": "https://www.espn.com/nfl/",
            "text": "All NFL News",
            "shortText": "All News",
            "isExternal": False,
            "isPremium": False,
        },
        "articles": [
            {
                "id": 48465811,
                "nowId": "1-48465811",
                "contentKey": "48465811-1-5-1",
                "dataSourceIdentifier": "99cd27db63ad8",
                "type": "HeadlineNews",
                "headline": "Ex-NFL WR Ted Ginn Jr. charged with DWI in Texas",
                "description": "Former NFL wide receiver and current Aviators coach Ted Ginn Jr. was charged with driving while intoxicated in Tarrant County, Texas, on Saturday.",
                "lastModified": "2026-04-12T18:33:03Z",
                "published": "2026-04-12T18:33:03Z",
                "images": [
                    {
                        "dataSourceIdentifier": "7ff7748b8175f",
                        "id": 48465749,
                        "type": "header",
                        "name": "Ted Ginn Jr. (April 12, 2026) [1296x729]",
                        "caption": "Ted Ginn Jr., who played 14 seasons in the NFL, is in his first season as the Columbus Aviators coach in the UFL.",
                        "credit": "Jason Mowry/UFL/Getty Images",
                        "height": 729,
                        "width": 1296,
                        "url": "https://a.espncdn.com/photo/2026/0412/r1642310_1296x729_16-9.jpg",
                    }
                ],
                "categories": [
                    {
                        "id": 409224,
                        "type": "topic",
                        "guid": "52313677-19f8-b106-ec91-d8d17e6087fe",
                        "description": "news",
                        "sportId": 0,
                        "topicId": 781,
                    },
                    {
                        "id": 9572,
                        "type": "league",
                        "uid": "s:20~l:28",
                        "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4",
                        "description": "NFL",
                        "sportId": 28,
                        "leagueId": 28,
                        "league": {
                            "id": 28,
                            "description": "NFL",
                            "abbreviation": "NFL",
                            "links": {
                                "web": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                                "mobile": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                            },
                        },
                    },
                    {
                        "id": 648933,
                        "type": "league",
                        "uid": "s:20~l:37",
                        "guid": "d6e52740-078b-31f0-84b2-c9962c5ce595",
                        "description": "UFL",
                        "sportId": 37,
                        "leagueId": 37,
                        "league": {
                            "id": 37,
                            "description": "UFL",
                            "abbreviation": "UFL",
                            "links": {
                                "web": {
                                    "leagues": {"href": "https://www.espn.com/ufl/"}
                                },
                                "mobile": {
                                    "leagues": {"href": "https://www.espn.com/ufl/"}
                                },
                            },
                        },
                    },
                    {
                        "id": 752956,
                        "type": "team",
                        "uid": "s:20~l:37~t:132261",
                        "guid": "220a2d62-fa10-307f-8251-5d8c60d72501",
                        "description": "Columbus Aviators",
                        "sportId": 37,
                        "teamId": 132261,
                        "team": {"id": 132261, "description": "Columbus Aviators"},
                    },
                    {"type": "guid", "guid": "52313677-19f8-b106-ec91-d8d17e6087fe"},
                    {"type": "guid", "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4"},
                    {"type": "guid", "guid": "d6e52740-078b-31f0-84b2-c9962c5ce595"},
                    {"type": "guid", "guid": "220a2d62-fa10-307f-8251-5d8c60d72501"},
                ],
                "premium": False,
                "links": {
                    "web": {
                        "href": "https://www.espn.com/united-football-league/story/_/id/48465811/ex-nfl-wr-ted-ginn-jr-charged-dwi-texas"
                    },
                    "mobile": {
                        "href": "http://m.espn.go.com/wireless/story?storyId=48465811"
                    },
                    "api": {
                        "self": {
                            "href": "https://content.core.api.espn.com/v1/sports/news/48465811"
                        }
                    },
                    "app": {
                        "sportscenter": {
                            "href": "sportscenter://x-callback-url/showStory?uid=48465811"
                        }
                    },
                },
            },
            {
                "id": 48465526,
                "nowId": "1-48465526",
                "contentKey": "48465526-1-293-1",
                "dataSourceIdentifier": "d5860160c2846",
                "type": "Media",
                "headline": "Emmanuel McNeil-Warren's NFL draft profile",
                "description": "Check out some of the top highlights from Toledo's Emmanuel McNeil-Warren.",
                "lastModified": "2026-04-12T13:50:01Z",
                "published": "2026-04-12T13:50:01Z",
                "images": [
                    {
                        "name": "Emmanuel McNeil-Warren's NFL draft profile",
                        "caption": "Check out some of the top highlights from Toledo's Emmanuel McNeil-Warren.",
                        "alt": "",
                        "height": 324,
                        "width": 576,
                        "url": "https://a.espncdn.com/media/motion/2026/0412/dm_260412_mcneil_warren/dm_260412_mcneil_warren.jpg",
                    }
                ],
                "categories": [
                    {
                        "id": 538704,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4837186",
                        "guid": "4f7f3680-fcb2-3a1f-a474-c578525bef08",
                        "description": "Emmanuel McNeil-Warren",
                        "sportId": 23,
                        "athleteId": 4837186,
                        "athlete": {
                            "id": 4837186,
                            "description": "Emmanuel McNeil-Warren",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4837186/emmanuel-mcneil-warren"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4837186/emmanuel-mcneil-warren"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 9571,
                        "type": "league",
                        "uid": "s:20~l:23",
                        "guid": "0f8e3d42-fa27-3f60-9e8d-276e4892f50e",
                        "description": "NCAA Football",
                        "sportId": 23,
                        "leagueId": 23,
                        "league": {
                            "id": 23,
                            "description": "NCAA Football",
                            "abbreviation": "NCAAF",
                            "links": {
                                "web": {
                                    "leagues": {
                                        "href": "https://www.espn.com/college-football/"
                                    }
                                },
                                "mobile": {
                                    "leagues": {
                                        "href": "https://www.espn.com/college-football/"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 9572,
                        "type": "league",
                        "uid": "s:20~l:28",
                        "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4",
                        "description": "NFL",
                        "sportId": 28,
                        "leagueId": 28,
                        "league": {
                            "id": 28,
                            "description": "NFL",
                            "abbreviation": "NFL",
                            "links": {
                                "web": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                                "mobile": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                            },
                        },
                    },
                    {
                        "id": 30937,
                        "type": "league",
                        "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec",
                        "description": "NFL Draft",
                        "sportId": 0,
                        "leagueId": 3400,
                        "league": {"id": 3400, "description": "NFL Draft"},
                    },
                    {
                        "id": 1142,
                        "type": "team",
                        "uid": "s:20~l:23~t:2649",
                        "guid": "fa2515be-1435-f76e-381c-1bde51bb4a64",
                        "description": "Toledo Rockets",
                        "sportId": 23,
                        "teamId": 2649,
                        "team": {
                            "id": 2649,
                            "description": "Toledo Rockets",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2649/toledo-rockets"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2649/toledo-rockets"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 2649,
                        "type": "team",
                        "guid": "c8c40f10-3586-3acc-8c02-5877fa5d1f34",
                        "description": "University of Toledo",
                        "sportId": 3170,
                        "teamId": 2649,
                        "team": {"id": 2649, "description": "University of Toledo"},
                    },
                    {"type": "guid", "guid": "4f7f3680-fcb2-3a1f-a474-c578525bef08"},
                    {"type": "guid", "guid": "0f8e3d42-fa27-3f60-9e8d-276e4892f50e"},
                    {"type": "guid", "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4"},
                    {"type": "guid", "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec"},
                    {"type": "guid", "guid": "fa2515be-1435-f76e-381c-1bde51bb4a64"},
                    {"type": "guid", "guid": "0d9f29bf-d4ee-36b1-aae2-65e84768e47d"},
                    {"type": "guid", "guid": "c8c40f10-3586-3acc-8c02-5877fa5d1f34"},
                ],
                "premium": False,
                "links": {
                    "web": {
                        "href": "https://www.espn.com/video/clip?id=48465526",
                        "self": {
                            "href": "https://www.espn.com/video/clip?id=48465526",
                            "dsi": {
                                "href": "https://www.espn.com/video/clip?id=d5860160c2846"
                            },
                        },
                    },
                    "api": {
                        "self": {
                            "href": "https://content.core.api.espn.com/v1/video/clips/48465526"
                        },
                        "artwork": {
                            "href": "https://artwork.api.espn.com/artwork/collections/media/f9245244-65c4-4ebc-add8-810f617a314d"
                        },
                    },
                    "sportscenter": {
                        "href": "sportscenter://x-callback-url/showVideo?videoID=48465526&videoDSI=d5860160c2846"
                    },
                },
            },
            {
                "id": 48443025,
                "nowId": "1-48443025",
                "contentKey": "48443025-1-6-1",
                "dataSourceIdentifier": "69316fa4eb1b4",
                "type": "Story",
                "headline": "2026 NFL draft risers: Seven prospects climbing boards",
                "description": "Dillon Thieneman and Monroe Freeling have drastically boosted their stock since the start of last season. Who else has climbed the board?",
                "lastModified": "2026-04-12T10:40:17Z",
                "published": "2026-04-12T10:40:17Z",
                "images": [
                    {
                        "dataSourceIdentifier": "fedd24e260383",
                        "id": 48450032,
                        "type": "header",
                        "name": "Dillon Thieneman for RISERS [608x342]",
                        "credit": "David Rosenblum/Icon Sportswire",
                        "height": 342,
                        "width": 608,
                        "url": "https://a.espncdn.com/photo/2026/0410/r1641544_608x342_16-9.jpg",
                    },
                    {
                        "type": "Media",
                        "name": "Monroe Freeling's NFL draft profile",
                        "caption": "Check out some of the top highlights from Georgia's Monroe Freeling.",
                        "height": 324,
                        "width": 576,
                        "url": "https://a.espncdn.com/media/motion/2026/0404/dm_260404_monroe_freeling_draft_reel/dm_260404_monroe_freeling_draft_reel.jpg",
                    },
                ],
                "categories": [
                    {
                        "id": 9572,
                        "type": "league",
                        "uid": "s:20~l:28",
                        "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4",
                        "description": "NFL",
                        "sportId": 28,
                        "leagueId": 28,
                        "league": {
                            "id": 28,
                            "description": "NFL",
                            "abbreviation": "NFL",
                            "links": {
                                "web": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                                "mobile": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                            },
                        },
                    },
                    {
                        "id": 30937,
                        "type": "league",
                        "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec",
                        "description": "NFL Draft",
                        "sportId": 0,
                        "leagueId": 3400,
                        "league": {"id": 3400, "description": "NFL Draft"},
                    },
                    {
                        "id": 1111,
                        "type": "team",
                        "uid": "s:20~l:23~t:2483",
                        "guid": "116d333f-cf1a-0c67-d450-36a834af56de",
                        "description": "Oregon Ducks",
                        "sportId": 23,
                        "teamId": 2483,
                        "team": {
                            "id": 2483,
                            "description": "Oregon Ducks",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2483/oregon-ducks"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2483/oregon-ducks"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 2483,
                        "type": "team",
                        "guid": "94cc8326-138d-3d76-8f6e-65e8744e6d92",
                        "description": "University of Oregon",
                        "sportId": 3170,
                        "teamId": 2483,
                        "team": {"id": 2483, "description": "University of Oregon"},
                    },
                    {
                        "id": 606457,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4954445",
                        "guid": "317d2e19-df14-3924-ad24-d745aadafad3",
                        "description": "Dillon Thieneman",
                        "sportId": 23,
                        "athleteId": 4954445,
                        "athlete": {
                            "id": 4954445,
                            "description": "Dillon Thieneman",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4954445/dillon-thieneman"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4954445/dillon-thieneman"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 1091,
                        "type": "team",
                        "uid": "s:20~l:23~t:61",
                        "guid": "4351fef8-fe69-53b1-ea57-72684b36ec35",
                        "description": "Georgia Bulldogs",
                        "sportId": 23,
                        "teamId": 61,
                        "team": {
                            "id": 61,
                            "description": "Georgia Bulldogs",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/61/georgia-bulldogs"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/61/georgia-bulldogs"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 61,
                        "type": "team",
                        "guid": "429cd0c4-212a-3660-9508-9e74776b5442",
                        "description": "University of Georgia",
                        "sportId": 3170,
                        "teamId": 61,
                        "team": {"id": 61, "description": "University of Georgia"},
                    },
                    {
                        "id": 605579,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4870694",
                        "guid": "04146b01-ba4a-3d1c-9208-aec23febb131",
                        "description": "Monroe Freeling",
                        "sportId": 23,
                        "athleteId": 4870694,
                        "athlete": {
                            "id": 4870694,
                            "description": "Monroe Freeling",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4870694/monroe-freeling"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4870694/monroe-freeling"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 1126,
                        "type": "team",
                        "uid": "s:20~l:23~t:2132",
                        "guid": "8e2c392d-d2c3-6a0f-2870-6a4487fc967f",
                        "description": "Cincinnati Bearcats",
                        "sportId": 23,
                        "teamId": 2132,
                        "team": {
                            "id": 2132,
                            "description": "Cincinnati Bearcats",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2132/cincinnati-bearcats"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2132/cincinnati-bearcats"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 2132,
                        "type": "team",
                        "guid": "2a9e6a6d-aa16-3525-a5f4-2aee8a1a77e6",
                        "description": "University of Cincinnati",
                        "sportId": 3170,
                        "teamId": 2132,
                        "team": {"id": 2132, "description": "University of Cincinnati"},
                    },
                    {
                        "id": 501588,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4885466",
                        "guid": "3b79a0b5-667a-34ac-8a5c-d67b45363beb",
                        "description": "Jeff Caldwell",
                        "sportId": 23,
                        "athleteId": 4885466,
                        "athlete": {
                            "id": 4885466,
                            "description": "Jeff Caldwell",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4885466/jeff-caldwell"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4885466/jeff-caldwell"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 1102,
                        "type": "team",
                        "uid": "s:20~l:23~t:9",
                        "guid": "d60a0d84-8fa8-2bdf-13ec-fb0f9deda94c",
                        "description": "Arizona State Sun Devils",
                        "sportId": 23,
                        "teamId": 9,
                        "team": {
                            "id": 9,
                            "description": "Arizona State Sun Devils",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/9/arizona-state-sun-devils"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/9/arizona-state-sun-devils"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 9,
                        "type": "team",
                        "guid": "7f6c3121-857d-3096-a4f1-f841da598230",
                        "description": "Arizona State University",
                        "sportId": 3170,
                        "teamId": 9,
                        "team": {"id": 9, "description": "Arizona State University"},
                    },
                    {
                        "id": 605019,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:5150136",
                        "guid": "34173f97-1414-3c47-9903-211a42f7f785",
                        "description": "Max Iheanachor",
                        "sportId": 23,
                        "athleteId": 5150136,
                        "athlete": {
                            "id": 5150136,
                            "description": "Max Iheanachor",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/5150136/max-iheanachor"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/5150136/max-iheanachor"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 77255,
                        "type": "team",
                        "uid": "s:20~l:23~t:2247",
                        "guid": "729c7315-1812-052c-1123-f44cf21b435c",
                        "description": "Georgia State Panthers",
                        "sportId": 23,
                        "teamId": 2247,
                        "team": {
                            "id": 2247,
                            "description": "Georgia State Panthers",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2247/georgia-state-panthers"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2247/georgia-state-panthers"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 2247,
                        "type": "team",
                        "guid": "c69dda12-fd85-386f-8fdb-b9f4783322cb",
                        "description": "Georgia State University",
                        "sportId": 3170,
                        "teamId": 2247,
                        "team": {"id": 2247, "description": "Georgia State University"},
                    },
                    {
                        "id": 672922,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:5220680",
                        "guid": "fcb8cea5-a51b-3b85-93fa-0f934f6e60ef",
                        "description": "Ted Hurst",
                        "sportId": 23,
                        "athleteId": 5220680,
                        "athlete": {
                            "id": 5220680,
                            "description": "Ted Hurst",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/5220680/ted-hurst"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/5220680/ted-hurst"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 1107,
                        "type": "team",
                        "uid": "s:20~l:23~t:30",
                        "guid": "63d7a1b4-ee19-f0ae-33c5-42a14e000fb8",
                        "description": "USC Trojans",
                        "sportId": 23,
                        "teamId": 30,
                        "team": {
                            "id": 30,
                            "description": "USC Trojans",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/30/usc-trojans"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/30/usc-trojans"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 30,
                        "type": "team",
                        "guid": "d3f426a4-56b8-3f15-8186-370c3af7daf8",
                        "description": "University of Southern California",
                        "sportId": 3170,
                        "teamId": 30,
                        "team": {
                            "id": 30,
                            "description": "University of Southern California",
                        },
                    },
                    {
                        "id": 491889,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4602656",
                        "guid": "32660e34-1146-3602-93c2-838a94aa6b7d",
                        "description": "Eric Gentry",
                        "sportId": 23,
                        "athleteId": 4602656,
                        "athlete": {
                            "id": 4602656,
                            "description": "Eric Gentry",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4602656/eric-gentry"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4602656/eric-gentry"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 14855,
                        "type": "team",
                        "uid": "s:20~l:23~t:2449",
                        "guid": "1ea4925c-7fb3-b48b-60c4-ed969feb6a1c",
                        "description": "North Dakota State Bison",
                        "sportId": 23,
                        "teamId": 2449,
                        "team": {
                            "id": 2449,
                            "description": "North Dakota State Bison",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2449/north-dakota-state-bison"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/college-football/team/_/id/2449/north-dakota-state-bison"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 2449,
                        "type": "team",
                        "guid": "6c366161-b99b-38ee-ac3c-1d2a658e54b2",
                        "description": "North Dakota State University",
                        "sportId": 3170,
                        "teamId": 2449,
                        "team": {
                            "id": 2449,
                            "description": "North Dakota State University",
                        },
                    },
                    {
                        "id": 496535,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4879256",
                        "guid": "7614b408-63dc-36c6-881c-b2fdc4aee39d",
                        "description": "Barika Kpeenu",
                        "sportId": 23,
                        "athleteId": 4879256,
                        "athlete": {
                            "id": 4879256,
                            "description": "Barika Kpeenu",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4879256/barika-kpeenu"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4879256/barika-kpeenu"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 9571,
                        "type": "league",
                        "uid": "s:20~l:23",
                        "guid": "0f8e3d42-fa27-3f60-9e8d-276e4892f50e",
                        "description": "NCAA Football",
                        "sportId": 23,
                        "leagueId": 23,
                        "league": {
                            "id": 23,
                            "description": "NCAA Football",
                            "abbreviation": "NCAAF",
                            "links": {
                                "web": {
                                    "leagues": {
                                        "href": "https://www.espn.com/college-football/"
                                    }
                                },
                                "mobile": {
                                    "leagues": {
                                        "href": "https://www.espn.com/college-football/"
                                    }
                                },
                            },
                        },
                    },
                    {"type": "guid", "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4"},
                    {"type": "guid", "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec"},
                    {"type": "guid", "guid": "116d333f-cf1a-0c67-d450-36a834af56de"},
                    {"type": "guid", "guid": "2bba3706-6f29-3e68-8b28-583a0d4a9caa"},
                    {"type": "guid", "guid": "94cc8326-138d-3d76-8f6e-65e8744e6d92"},
                    {"type": "guid", "guid": "317d2e19-df14-3924-ad24-d745aadafad3"},
                    {"type": "guid", "guid": "4351fef8-fe69-53b1-ea57-72684b36ec35"},
                    {"type": "guid", "guid": "2845c2f1-d2ef-3f34-aaa2-469687c28cec"},
                    {"type": "guid", "guid": "429cd0c4-212a-3660-9508-9e74776b5442"},
                    {"type": "guid", "guid": "04146b01-ba4a-3d1c-9208-aec23febb131"},
                    {"type": "guid", "guid": "8e2c392d-d2c3-6a0f-2870-6a4487fc967f"},
                    {"type": "guid", "guid": "057d08ff-5067-3b91-946b-d941c8aecde5"},
                    {"type": "guid", "guid": "2a9e6a6d-aa16-3525-a5f4-2aee8a1a77e6"},
                    {"type": "guid", "guid": "3b79a0b5-667a-34ac-8a5c-d67b45363beb"},
                    {"type": "guid", "guid": "d60a0d84-8fa8-2bdf-13ec-fb0f9deda94c"},
                    {"type": "guid", "guid": "7f6c3121-857d-3096-a4f1-f841da598230"},
                    {"type": "guid", "guid": "34173f97-1414-3c47-9903-211a42f7f785"},
                    {"type": "guid", "guid": "729c7315-1812-052c-1123-f44cf21b435c"},
                    {"type": "guid", "guid": "f275f7f7-d9a7-33aa-b446-81b016a0e754"},
                    {"type": "guid", "guid": "c69dda12-fd85-386f-8fdb-b9f4783322cb"},
                    {"type": "guid", "guid": "fcb8cea5-a51b-3b85-93fa-0f934f6e60ef"},
                    {"type": "guid", "guid": "63d7a1b4-ee19-f0ae-33c5-42a14e000fb8"},
                    {"type": "guid", "guid": "d3f426a4-56b8-3f15-8186-370c3af7daf8"},
                    {"type": "guid", "guid": "32660e34-1146-3602-93c2-838a94aa6b7d"},
                    {"type": "guid", "guid": "1ea4925c-7fb3-b48b-60c4-ed969feb6a1c"},
                    {"type": "guid", "guid": "1d698a9d-bb50-3ad4-9a1a-30b3de3a9b45"},
                    {"type": "guid", "guid": "6c366161-b99b-38ee-ac3c-1d2a658e54b2"},
                    {"type": "guid", "guid": "7614b408-63dc-36c6-881c-b2fdc4aee39d"},
                    {"type": "guid", "guid": "0f8e3d42-fa27-3f60-9e8d-276e4892f50e"},
                ],
                "premium": False,
                "links": {
                    "web": {
                        "href": "https://www.espn.com/nfl/draft2026/story/_/id/48443025/2026-nfl-draft-risers-prospects-freeling-thieneman-iheanachor"
                    },
                    "mobile": {
                        "href": "http://m.espn.go.com/nfl/story?storyId=48443025"
                    },
                    "api": {
                        "self": {
                            "href": "https://content.core.api.espn.com/v1/sports/news/48443025"
                        }
                    },
                    "app": {
                        "sportscenter": {
                            "href": "sportscenter://x-callback-url/showStory?uid=48443025"
                        }
                    },
                },
                "byline": "Jeff Legwold",
            },
            {
                "id": 48440687,
                "nowId": "1-48440687",
                "contentKey": "48440687-1-6-1",
                "dataSourceIdentifier": "55f453e3c6d74",
                "type": "Story",
                "headline": "Why Keyshawn Johnson was the last WR to go No. 1, 30 years ago",
                "description": "The 1996 draft didn't produce a first-round QB, but the Jets found a playmaker with star power in Johnson.",
                "lastModified": "2026-04-12T10:16:01Z",
                "published": "2026-04-12T10:16:01Z",
                "images": [
                    {
                        "dataSourceIdentifier": "535233889d6a0",
                        "id": 48420875,
                        "type": "header",
                        "name": "It has been 30 years since the last WR went No. 1 overall ... will it ever happen again? [1500x844]",
                        "caption": "It has been 30 years since the last WR went No. 1 overall ... will it ever happen again? Here's why the Jets decided to make that investment in Keyshawn Johnson.",
                        "alt": "New York Jets and Keyshawn Johnson",
                        "credit": "Illustration by ESPN",
                        "height": 844,
                        "width": 1500,
                        "url": "https://a.espncdn.com/photo/2026/0407/nfl_30-years-wr-first-pick_fc_16x9.jpg",
                    },
                    {
                        "dataSourceIdentifier": "88e8238d46431",
                        "id": 48440949,
                        "type": "header",
                        "name": "Keyshawn Johnson USC [1296x729]",
                        "caption": "Mel Kiper said he received a phone call from Johnson in 1995, inquiring about his draft prospects. When told he'd probably be a first-round pick but probably not a high first-rounder, Johnson decided to return to USC for another year.",
                        "credit": "Richard Mackson/Sports Illustrated via Getty Images",
                        "height": 729,
                        "width": 1296,
                        "url": "https://a.espncdn.com/photo/2026/0409/r1641032_1296x729_16-9.jpg",
                    },
                    {
                        "dataSourceIdentifier": "3ebcab753ad92",
                        "id": 48440928,
                        "type": "header",
                        "name": "Keyshawn Johnson Jets [1296x729]",
                        "caption": "Johnson brought his star power to New York, making headlines with his brash personality and delivering on the field. He was an integral part of the team's turnaround in 1997.",
                        "credit": "Al Pereira/Michael Ochs Archives/Getty Images",
                        "height": 729,
                        "width": 1296,
                        "url": "https://a.espncdn.com/photo/2026/0409/r1641033_1296x729_16-9.jpg",
                    },
                    {
                        "dataSourceIdentifier": "54eac31913743",
                        "id": 48457531,
                        "type": "header",
                        "name": "NFL Draft photodesk [1296x729]",
                        "caption": "Jets fans wanted the star from Los Angeles, who blended Hollywood with Broadway and turned the field into his stage.",
                        "credit": "Manny Millan/Getty Images",
                        "height": 729,
                        "width": 1296,
                        "url": "https://a.espncdn.com/photo/2026/0411/r1641913_1296x729_16-9.jpg",
                    },
                ],
                "categories": [
                    {
                        "id": 30937,
                        "type": "league",
                        "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec",
                        "description": "NFL Draft",
                        "sportId": 0,
                        "leagueId": 3400,
                        "league": {"id": 3400, "description": "NFL Draft"},
                    },
                    {
                        "id": 9572,
                        "type": "league",
                        "uid": "s:20~l:28",
                        "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4",
                        "description": "NFL",
                        "sportId": 28,
                        "leagueId": 28,
                        "league": {
                            "id": 28,
                            "description": "NFL",
                            "abbreviation": "NFL",
                            "links": {
                                "web": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                                "mobile": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                            },
                        },
                    },
                    {
                        "id": 2378,
                        "type": "team",
                        "uid": "s:20~l:28~t:20",
                        "guid": "732d3caf-b350-1e34-48c6-b7cebb4a0d88",
                        "description": "New York Jets",
                        "sportId": 28,
                        "teamId": 20,
                        "team": {
                            "id": 20,
                            "description": "New York Jets",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/nfl/team/_/name/nyj/new-york-jets"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/nfl/team/_/name/nyj/new-york-jets"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 696437,
                        "type": "contributor",
                        "guid": "2f2acd9c-9576-37d0-bec4-acb019376e84",
                        "description": "Rich Cimini",
                        "slug": "rich-cimini",
                        "contributor": {"id": 1872, "description": "Rich Cimini"},
                    },
                    {"type": "guid", "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec"},
                    {"type": "guid", "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4"},
                    {"type": "guid", "guid": "732d3caf-b350-1e34-48c6-b7cebb4a0d88"},
                    {"type": "guid", "guid": "2f2acd9c-9576-37d0-bec4-acb019376e84"},
                ],
                "premium": False,
                "links": {
                    "web": {
                        "href": "https://www.espn.com/nfl/story/_/id/48440687/nfl-draft-keyshawn-johnson-was-last-wr-go-no-1-30-years-ago-new-york-jets"
                    },
                    "mobile": {
                        "href": "http://m.espn.go.com/nfl/story?storyId=48440687"
                    },
                    "api": {
                        "self": {
                            "href": "https://content.core.api.espn.com/v1/sports/news/48440687"
                        }
                    },
                    "app": {
                        "sportscenter": {
                            "href": "sportscenter://x-callback-url/showStory?uid=48440687"
                        }
                    },
                },
                "byline": "Rich Cimini",
            },
            {
                "id": 48457356,
                "nowId": "1-48457356",
                "contentKey": "48457356-1-6-1",
                "dataSourceIdentifier": "fb2f222ae06d5",
                "type": "Story",
                "headline": "Will Jets get defensive at No. 2 with edge David Bailey?",
                "description": "The Jets have never taken a defensive player as high as No. 2, but Bailey is not an ordinary edge rusher.",
                "lastModified": "2026-04-12T10:16:42Z",
                "published": "2026-04-12T10:16:42Z",
                "images": [
                    {
                        "dataSourceIdentifier": "74e140bb43dee",
                        "id": 48457395,
                        "type": "header",
                        "name": "David Bailey [1296x729]",
                        "caption": "Texas Tech edge rusher David Bailey recorded 154 pressures in 823 pass rushes over 48 career games (34 for Stanford, 14 for Texas Tech), which computes to an 18.7% pressure rate -- tops among FBS players since 2016.",
                        "credit": "AP Photo/Julio Cortez",
                        "height": 729,
                        "width": 1296,
                        "url": "https://a.espncdn.com/photo/2026/0411/r1641910_1296x729_16-9.jpg",
                    },
                    {
                        "type": "Media",
                        "name": "Kevin Clark: Sonny Styles is the best player in the 2026 NFL draft",
                        "caption": "Kevin Clark details why Ohio State linebacker Sonny Styles will be the best player in the 2026 NFL draft class.",
                        "height": 324,
                        "width": 576,
                        "url": "https://a.espncdn.com/media/motion/2026/0410/1bc4dc4c3f86420b9bc9f04744333972513/1bc4dc4c3f86420b9bc9f04744333972513.jpg",
                    },
                ],
                "categories": [
                    {
                        "id": 9572,
                        "type": "league",
                        "uid": "s:20~l:28",
                        "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4",
                        "description": "NFL",
                        "sportId": 28,
                        "leagueId": 28,
                        "league": {
                            "id": 28,
                            "description": "NFL",
                            "abbreviation": "NFL",
                            "links": {
                                "web": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                                "mobile": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                            },
                        },
                    },
                    {
                        "id": 30937,
                        "type": "league",
                        "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec",
                        "description": "NFL Draft",
                        "sportId": 0,
                        "leagueId": 3400,
                        "league": {"id": 3400, "description": "NFL Draft"},
                    },
                    {
                        "id": 2378,
                        "type": "team",
                        "uid": "s:20~l:28~t:20",
                        "guid": "732d3caf-b350-1e34-48c6-b7cebb4a0d88",
                        "description": "New York Jets",
                        "sportId": 28,
                        "teamId": 20,
                        "team": {
                            "id": 20,
                            "description": "New York Jets",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/nfl/team/_/name/nyj/new-york-jets"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/nfl/team/_/name/nyj/new-york-jets"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 696437,
                        "type": "contributor",
                        "guid": "2f2acd9c-9576-37d0-bec4-acb019376e84",
                        "description": "Rich Cimini",
                        "slug": "rich-cimini",
                        "contributor": {"id": 1872, "description": "Rich Cimini"},
                    },
                    {"type": "guid", "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4"},
                    {"type": "guid", "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec"},
                    {"type": "guid", "guid": "732d3caf-b350-1e34-48c6-b7cebb4a0d88"},
                    {"type": "guid", "guid": "2f2acd9c-9576-37d0-bec4-acb019376e84"},
                ],
                "premium": False,
                "links": {
                    "web": {
                        "href": "https://www.espn.com/nfl/story/_/id/48457356/will-jets-get-defensive-no-2-edge-david-bailey"
                    },
                    "mobile": {
                        "href": "http://m.espn.go.com/nfl/story?storyId=48457356"
                    },
                    "api": {
                        "self": {
                            "href": "https://content.core.api.espn.com/v1/sports/news/48457356"
                        }
                    },
                    "app": {
                        "sportscenter": {
                            "href": "sportscenter://x-callback-url/showStory?uid=48457356"
                        }
                    },
                },
                "byline": "Rich Cimini",
            },
            {
                "id": 48451661,
                "nowId": "1-48451661",
                "contentKey": "48451661-1-6-1",
                "dataSourceIdentifier": "27686dca584ce",
                "type": "Story",
                "headline": "Former Belichick aide brings insight to Patriots' No. 31 pick",
                "description": "Ernie Adams and the Belichick-led Patriots picked at bottom of Round 1 many times. Adams shares the strategy.",
                "lastModified": "2026-04-12T10:00:02Z",
                "published": "2026-04-12T10:00:02Z",
                "images": [
                    {
                        "dataSourceIdentifier": "09601a750c724",
                        "id": 48451697,
                        "type": "header",
                        "name": "Patriots pick is in [608x342]",
                        "credit": "John Smolek/Icon Sportswire)",
                        "height": 342,
                        "width": 608,
                        "url": "https://a.espncdn.com/photo/2026/0410/r1641675_608x342_16-9.jpg",
                    },
                    {
                        "dataSourceIdentifier": "cab7a2510c06c",
                        "id": 48451768,
                        "type": "header",
                        "name": "Ernie Adams [608x342]",
                        "caption": "Adams, right, spent over 20 years with the Patriots and Bill Belichick as a football research director.",
                        "credit": "AP Photo/Steven Senne, File)",
                        "height": 342,
                        "width": 608,
                        "url": "https://a.espncdn.com/photo/2026/0410/r1641677_608x342_16-9.jpg",
                    },
                    {
                        "type": "Media",
                        "name": "Patriots moving on from Mapu shines light on linebacker position",
                        "caption": "Mike Reiss reports on the Patriots' linebacker depth after moving on from Marte Mapu.",
                        "height": 324,
                        "width": 576,
                        "url": "https://a.espncdn.com/media/motion/2026/0407/dm_260407_Patriots_moving_on_from_Mapu_shines_light_on_linebacker_position/dm_260407_Patriots_moving_on_from_Mapu_shines_light_on_linebacker_position.jpg",
                    },
                ],
                "categories": [
                    {
                        "id": 9572,
                        "type": "league",
                        "uid": "s:20~l:28",
                        "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4",
                        "description": "NFL",
                        "sportId": 28,
                        "leagueId": 28,
                        "league": {
                            "id": 28,
                            "description": "NFL",
                            "abbreviation": "NFL",
                            "links": {
                                "web": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                                "mobile": {
                                    "leagues": {"href": "https://www.espn.com/nfl/"}
                                },
                            },
                        },
                    },
                    {
                        "id": 30937,
                        "type": "league",
                        "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec",
                        "description": "NFL Draft",
                        "sportId": 0,
                        "leagueId": 3400,
                        "league": {"id": 3400, "description": "NFL Draft"},
                    },
                    {
                        "id": 2321,
                        "type": "team",
                        "uid": "s:20~l:28~t:17",
                        "guid": "0078f353-fe3e-67ed-a42c-43cca0568e21",
                        "description": "New England Patriots",
                        "sportId": 28,
                        "teamId": 17,
                        "team": {
                            "id": 17,
                            "description": "New England Patriots",
                            "links": {
                                "web": {
                                    "teams": {
                                        "href": "https://www.espn.com/nfl/team/_/name/ne/new-england-patriots"
                                    }
                                },
                                "mobile": {
                                    "teams": {
                                        "href": "https://www.espn.com/nfl/team/_/name/ne/new-england-patriots"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 396760,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4429582",
                        "guid": "09beee77-ea78-15ba-d273-b3e664772873",
                        "description": "Joe Fagnano",
                        "sportId": 23,
                        "athleteId": 4429582,
                        "athlete": {
                            "id": 4429582,
                            "description": "Joe Fagnano",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4429582/joe-fagnano"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4429582/joe-fagnano"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 440164,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4596472",
                        "guid": "aaab6e81-bfa6-3ceb-bb91-e9e31a23552b",
                        "description": "Jalon Daniels",
                        "sportId": 23,
                        "athleteId": 4596472,
                        "athlete": {
                            "id": 4596472,
                            "description": "Jalon Daniels",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4596472/jalon-daniels"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4596472/jalon-daniels"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 497646,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4683471",
                        "guid": "3b12aa24-b869-3e4f-8559-4707d1ad13b3",
                        "description": "Brady Olson",
                        "sportId": 23,
                        "athleteId": 4683471,
                        "athlete": {
                            "id": 4683471,
                            "description": "Brady Olson",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4683471/brady-olson"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4683471/brady-olson"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 442648,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4433938",
                        "guid": "54e1c897-5d32-358d-ab4e-40eaa608b8c2",
                        "description": "Jeremiah Wright",
                        "sportId": 23,
                        "athleteId": 4433938,
                        "athlete": {
                            "id": 4433938,
                            "description": "Jeremiah Wright",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4433938/jeremiah-wright"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4433938/jeremiah-wright"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 492513,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4708238",
                        "guid": "aea46227-3b76-30fd-99a8-c9c4f4164d1d",
                        "description": "George Gumbs Jr",
                        "sportId": 23,
                        "athleteId": 4708238,
                        "athlete": {
                            "id": 4708238,
                            "description": "George Gumbs Jr",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4708238/george-gumbs-jr"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4708238/george-gumbs-jr"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 605551,
                        "type": "athlete",
                        "uid": "s:20~l:23~a:4870707",
                        "guid": "e35afc8b-9bf2-3f13-aa5e-a762e7de39cb",
                        "description": "Keldric Faulk",
                        "sportId": 23,
                        "athleteId": 4870707,
                        "athlete": {
                            "id": 4870707,
                            "description": "Keldric Faulk",
                            "links": {
                                "web": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4870707/keldric-faulk"
                                    }
                                },
                                "mobile": {
                                    "athletes": {
                                        "href": "https://www.espn.com/college-football/player/_/id/4870707/keldric-faulk"
                                    }
                                },
                            },
                        },
                    },
                    {
                        "id": 696440,
                        "type": "contributor",
                        "guid": "bdee10fe-a1a2-3ced-87dd-43089bf47931",
                        "description": "Mike Reiss",
                        "slug": "mike-reiss",
                        "contributor": {"id": 1800, "description": "Mike Reiss"},
                    },
                    {"type": "guid", "guid": "ad4c3bd2-ddb6-3f8c-8abf-744855a08fa4"},
                    {"type": "guid", "guid": "4509a056-5f02-4fb8-b6bb-de7cc5a923ec"},
                    {"type": "guid", "guid": "0078f353-fe3e-67ed-a42c-43cca0568e21"},
                    {"type": "guid", "guid": "09beee77-ea78-15ba-d273-b3e664772873"},
                    {"type": "guid", "guid": "aaab6e81-bfa6-3ceb-bb91-e9e31a23552b"},
                    {"type": "guid", "guid": "3b12aa24-b869-3e4f-8559-4707d1ad13b3"},
                    {"type": "guid", "guid": "54e1c897-5d32-358d-ab4e-40eaa608b8c2"},
                    {"type": "guid", "guid": "aea46227-3b76-30fd-99a8-c9c4f4164d1d"},
                    {"type": "guid", "guid": "e35afc8b-9bf2-3f13-aa5e-a762e7de39cb"},
                    {"type": "guid", "guid": "bdee10fe-a1a2-3ced-87dd-43089bf47931"},
                ],
                "premium": False,
                "links": {
                    "web": {
                        "href": "https://www.espn.com/nfl/story/_/id/48451661/new-england-patriots-31-overall-pick-nfl-draft-bill-belichick-ernie-adams-insight-notebook"
                    },
                    "mobile": {
                        "href": "http://m.espn.go.com/nfl/story?storyId=48451661"
                    },
                    "api": {
                        "self": {
                            "href": "https://content.core.api.espn.com/v1/sports/news/48451661"
                        }
                    },
                    "app": {
                        "sportscenter": {
                            "href": "sportscenter://x-callback-url/showStory?uid=48451661"
                        }
                    },
                },
                "byline": "Mike Reiss",
            },
        ],
    },
    "videos": [],
    "wallclockAvailable": False,
    "meta": {
        "gp_topic": "gp-football-nfl-190920006",
        "gameSwitcherEnabled": False,
        "picker_topic": "picker-football-nfl",
        "gameState": "post",
    },
    "standings": {
        "fullViewLink": {
            "text": "Full Standings",
            "href": "https://www.espn.com/nfl/standings",
        },
        "header": "2025 Standings",
        "groups": [
            {
                "standings": {
                    "entries": [
                        {
                            "team": "Carolina",
                            "link": "https://www.espn.com/nfl/team/_/name/car/carolina-panthers",
                            "id": "29",
                            "uid": "s:20~l:28~t:29",
                            "stats": [
                                {
                                    "name": "losses",
                                    "displayName": "Losses",
                                    "shortDisplayName": "L",
                                    "description": "Losses",
                                    "abbreviation": "L",
                                    "type": "losses",
                                    "value": 9.0,
                                    "displayValue": "9",
                                },
                                {
                                    "name": "pointsAgainst",
                                    "displayName": "Points Against",
                                    "shortDisplayName": "PA",
                                    "description": "Total Points Against",
                                    "abbreviation": "PA",
                                    "type": "pointsagainst",
                                    "value": 380.0,
                                    "displayValue": "380",
                                },
                                {
                                    "name": "pointsFor",
                                    "displayName": "Points For",
                                    "shortDisplayName": "PF",
                                    "description": "Total Points For",
                                    "abbreviation": "PF",
                                    "type": "pointsfor",
                                    "value": 311.0,
                                    "displayValue": "311",
                                },
                                {
                                    "name": "ties",
                                    "displayName": "Ties",
                                    "shortDisplayName": "T",
                                    "description": "Ties",
                                    "abbreviation": "T",
                                    "type": "ties",
                                    "value": 0.0,
                                    "displayValue": "0",
                                },
                                {
                                    "name": "winPercent",
                                    "displayName": "Win Percentage",
                                    "shortDisplayName": "PCT",
                                    "description": "Winning Percentage",
                                    "abbreviation": "PCT",
                                    "type": "winpercent",
                                    "value": 0.47058824,
                                    "displayValue": ".471",
                                },
                                {
                                    "name": "wins",
                                    "displayName": "Wins",
                                    "shortDisplayName": "W",
                                    "description": "Wins",
                                    "abbreviation": "W",
                                    "type": "wins",
                                    "value": 8.0,
                                    "displayValue": "8",
                                },
                                {
                                    "id": "0",
                                    "name": "overall",
                                    "abbreviation": "Any",
                                    "type": "total",
                                    "summary": "8-9",
                                    "displayValue": "8-9",
                                },
                            ],
                            "logo": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/car.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:45Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/car.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:45Z",
                                },
                            ],
                        },
                        {
                            "team": "Tampa Bay",
                            "link": "https://www.espn.com/nfl/team/_/name/tb/tampa-bay-buccaneers",
                            "id": "27",
                            "uid": "s:20~l:28~t:27",
                            "stats": [
                                {
                                    "name": "losses",
                                    "displayName": "Losses",
                                    "shortDisplayName": "L",
                                    "description": "Losses",
                                    "abbreviation": "L",
                                    "type": "losses",
                                    "value": 9.0,
                                    "displayValue": "9",
                                },
                                {
                                    "name": "pointsAgainst",
                                    "displayName": "Points Against",
                                    "shortDisplayName": "PA",
                                    "description": "Total Points Against",
                                    "abbreviation": "PA",
                                    "type": "pointsagainst",
                                    "value": 411.0,
                                    "displayValue": "411",
                                },
                                {
                                    "name": "pointsFor",
                                    "displayName": "Points For",
                                    "shortDisplayName": "PF",
                                    "description": "Total Points For",
                                    "abbreviation": "PF",
                                    "type": "pointsfor",
                                    "value": 380.0,
                                    "displayValue": "380",
                                },
                                {
                                    "name": "ties",
                                    "displayName": "Ties",
                                    "shortDisplayName": "T",
                                    "description": "Ties",
                                    "abbreviation": "T",
                                    "type": "ties",
                                    "value": 0.0,
                                    "displayValue": "0",
                                },
                                {
                                    "name": "winPercent",
                                    "displayName": "Win Percentage",
                                    "shortDisplayName": "PCT",
                                    "description": "Winning Percentage",
                                    "abbreviation": "PCT",
                                    "type": "winpercent",
                                    "value": 0.47058824,
                                    "displayValue": ".471",
                                },
                                {
                                    "name": "wins",
                                    "displayName": "Wins",
                                    "shortDisplayName": "W",
                                    "description": "Wins",
                                    "abbreviation": "W",
                                    "type": "wins",
                                    "value": 8.0,
                                    "displayValue": "8",
                                },
                                {
                                    "id": "0",
                                    "name": "overall",
                                    "abbreviation": "Any",
                                    "type": "total",
                                    "summary": "8-9",
                                    "displayValue": "8-9",
                                },
                            ],
                            "logo": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/tb.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:57Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/tb.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:57Z",
                                },
                            ],
                        },
                        {
                            "team": "Atlanta",
                            "link": "https://www.espn.com/nfl/team/_/name/atl/atlanta-falcons",
                            "id": "1",
                            "uid": "s:20~l:28~t:1",
                            "stats": [
                                {
                                    "name": "losses",
                                    "displayName": "Losses",
                                    "shortDisplayName": "L",
                                    "description": "Losses",
                                    "abbreviation": "L",
                                    "type": "losses",
                                    "value": 9.0,
                                    "displayValue": "9",
                                },
                                {
                                    "name": "pointsAgainst",
                                    "displayName": "Points Against",
                                    "shortDisplayName": "PA",
                                    "description": "Total Points Against",
                                    "abbreviation": "PA",
                                    "type": "pointsagainst",
                                    "value": 401.0,
                                    "displayValue": "401",
                                },
                                {
                                    "name": "pointsFor",
                                    "displayName": "Points For",
                                    "shortDisplayName": "PF",
                                    "description": "Total Points For",
                                    "abbreviation": "PF",
                                    "type": "pointsfor",
                                    "value": 353.0,
                                    "displayValue": "353",
                                },
                                {
                                    "name": "ties",
                                    "displayName": "Ties",
                                    "shortDisplayName": "T",
                                    "description": "Ties",
                                    "abbreviation": "T",
                                    "type": "ties",
                                    "value": 0.0,
                                    "displayValue": "0",
                                },
                                {
                                    "name": "winPercent",
                                    "displayName": "Win Percentage",
                                    "shortDisplayName": "PCT",
                                    "description": "Winning Percentage",
                                    "abbreviation": "PCT",
                                    "type": "winpercent",
                                    "value": 0.47058824,
                                    "displayValue": ".471",
                                },
                                {
                                    "name": "wins",
                                    "displayName": "Wins",
                                    "shortDisplayName": "W",
                                    "description": "Wins",
                                    "abbreviation": "W",
                                    "type": "wins",
                                    "value": 8.0,
                                    "displayValue": "8",
                                },
                                {
                                    "id": "0",
                                    "name": "overall",
                                    "abbreviation": "Any",
                                    "type": "total",
                                    "summary": "8-9",
                                    "displayValue": "8-9",
                                },
                            ],
                            "logo": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:44Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/atl.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:44Z",
                                },
                            ],
                        },
                        {
                            "team": "New Orleans",
                            "link": "https://www.espn.com/nfl/team/_/name/no/new-orleans-saints",
                            "id": "18",
                            "uid": "s:20~l:28~t:18",
                            "stats": [
                                {
                                    "name": "losses",
                                    "displayName": "Losses",
                                    "shortDisplayName": "L",
                                    "description": "Losses",
                                    "abbreviation": "L",
                                    "type": "losses",
                                    "value": 11.0,
                                    "displayValue": "11",
                                },
                                {
                                    "name": "pointsAgainst",
                                    "displayName": "Points Against",
                                    "shortDisplayName": "PA",
                                    "description": "Total Points Against",
                                    "abbreviation": "PA",
                                    "type": "pointsagainst",
                                    "value": 383.0,
                                    "displayValue": "383",
                                },
                                {
                                    "name": "pointsFor",
                                    "displayName": "Points For",
                                    "shortDisplayName": "PF",
                                    "description": "Total Points For",
                                    "abbreviation": "PF",
                                    "type": "pointsfor",
                                    "value": 306.0,
                                    "displayValue": "306",
                                },
                                {
                                    "name": "ties",
                                    "displayName": "Ties",
                                    "shortDisplayName": "T",
                                    "description": "Ties",
                                    "abbreviation": "T",
                                    "type": "ties",
                                    "value": 0.0,
                                    "displayValue": "0",
                                },
                                {
                                    "name": "winPercent",
                                    "displayName": "Win Percentage",
                                    "shortDisplayName": "PCT",
                                    "description": "Winning Percentage",
                                    "abbreviation": "PCT",
                                    "type": "winpercent",
                                    "value": 0.3529412,
                                    "displayValue": ".353",
                                },
                                {
                                    "name": "wins",
                                    "displayName": "Wins",
                                    "shortDisplayName": "W",
                                    "description": "Wins",
                                    "abbreviation": "W",
                                    "type": "wins",
                                    "value": 6.0,
                                    "displayValue": "6",
                                },
                                {
                                    "id": "0",
                                    "name": "overall",
                                    "abbreviation": "Any",
                                    "type": "total",
                                    "summary": "6-11",
                                    "displayValue": "6-11",
                                },
                            ],
                            "logo": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/no.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:54Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/no.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:54Z",
                                },
                            ],
                        },
                    ]
                },
                "header": "2025 NFC South Standings",
                "href": "https://www.espn.com/nfl/standings/_/group/11",
                "conferenceHeader": "National Football Conference",
                "divisionHeader": "NFC South",
            },
            {
                "standings": {
                    "entries": [
                        {
                            "team": "Philadelphia",
                            "link": "https://www.espn.com/nfl/team/_/name/phi/philadelphia-eagles",
                            "id": "21",
                            "uid": "s:20~l:28~t:21",
                            "stats": [
                                {
                                    "name": "losses",
                                    "displayName": "Losses",
                                    "shortDisplayName": "L",
                                    "description": "Losses",
                                    "abbreviation": "L",
                                    "type": "losses",
                                    "value": 6.0,
                                    "displayValue": "6",
                                },
                                {
                                    "name": "pointsAgainst",
                                    "displayName": "Points Against",
                                    "shortDisplayName": "PA",
                                    "description": "Total Points Against",
                                    "abbreviation": "PA",
                                    "type": "pointsagainst",
                                    "value": 325.0,
                                    "displayValue": "325",
                                },
                                {
                                    "name": "pointsFor",
                                    "displayName": "Points For",
                                    "shortDisplayName": "PF",
                                    "description": "Total Points For",
                                    "abbreviation": "PF",
                                    "type": "pointsfor",
                                    "value": 379.0,
                                    "displayValue": "379",
                                },
                                {
                                    "name": "ties",
                                    "displayName": "Ties",
                                    "shortDisplayName": "T",
                                    "description": "Ties",
                                    "abbreviation": "T",
                                    "type": "ties",
                                    "value": 0.0,
                                    "displayValue": "0",
                                },
                                {
                                    "name": "winPercent",
                                    "displayName": "Win Percentage",
                                    "shortDisplayName": "PCT",
                                    "description": "Winning Percentage",
                                    "abbreviation": "PCT",
                                    "type": "winpercent",
                                    "value": 0.64705884,
                                    "displayValue": ".647",
                                },
                                {
                                    "name": "wins",
                                    "displayName": "Wins",
                                    "shortDisplayName": "W",
                                    "description": "Wins",
                                    "abbreviation": "W",
                                    "type": "wins",
                                    "value": 11.0,
                                    "displayValue": "11",
                                },
                                {
                                    "id": "0",
                                    "name": "overall",
                                    "abbreviation": "Any",
                                    "type": "total",
                                    "summary": "11-6",
                                    "displayValue": "11-6",
                                },
                            ],
                            "logo": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:55Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/phi.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:56Z",
                                },
                            ],
                        },
                        {
                            "team": "Dallas",
                            "link": "https://www.espn.com/nfl/team/_/name/dal/dallas-cowboys",
                            "id": "6",
                            "uid": "s:20~l:28~t:6",
                            "stats": [
                                {
                                    "name": "losses",
                                    "displayName": "Losses",
                                    "shortDisplayName": "L",
                                    "description": "Losses",
                                    "abbreviation": "L",
                                    "type": "losses",
                                    "value": 9.0,
                                    "displayValue": "9",
                                },
                                {
                                    "name": "pointsAgainst",
                                    "displayName": "Points Against",
                                    "shortDisplayName": "PA",
                                    "description": "Total Points Against",
                                    "abbreviation": "PA",
                                    "type": "pointsagainst",
                                    "value": 511.0,
                                    "displayValue": "511",
                                },
                                {
                                    "name": "pointsFor",
                                    "displayName": "Points For",
                                    "shortDisplayName": "PF",
                                    "description": "Total Points For",
                                    "abbreviation": "PF",
                                    "type": "pointsfor",
                                    "value": 471.0,
                                    "displayValue": "471",
                                },
                                {
                                    "name": "ties",
                                    "displayName": "Ties",
                                    "shortDisplayName": "T",
                                    "description": "Ties",
                                    "abbreviation": "T",
                                    "type": "ties",
                                    "value": 1.0,
                                    "displayValue": "1",
                                },
                                {
                                    "name": "winPercent",
                                    "displayName": "Win Percentage",
                                    "shortDisplayName": "PCT",
                                    "description": "Winning Percentage",
                                    "abbreviation": "PCT",
                                    "type": "winpercent",
                                    "value": 0.44117647,
                                    "displayValue": ".441",
                                },
                                {
                                    "name": "wins",
                                    "displayName": "Wins",
                                    "shortDisplayName": "W",
                                    "description": "Wins",
                                    "abbreviation": "W",
                                    "type": "wins",
                                    "value": 7.0,
                                    "displayValue": "7",
                                },
                                {
                                    "id": "0",
                                    "name": "overall",
                                    "abbreviation": "Any",
                                    "type": "total",
                                    "summary": "7-9-1",
                                    "displayValue": "7-9-1",
                                },
                            ],
                            "logo": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:47Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/dal.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:59Z",
                                },
                            ],
                        },
                        {
                            "team": "Washington",
                            "link": "https://www.espn.com/nfl/team/_/name/wsh/washington-commanders",
                            "id": "28",
                            "uid": "s:20~l:28~t:28",
                            "stats": [
                                {
                                    "name": "losses",
                                    "displayName": "Losses",
                                    "shortDisplayName": "L",
                                    "description": "Losses",
                                    "abbreviation": "L",
                                    "type": "losses",
                                    "value": 12.0,
                                    "displayValue": "12",
                                },
                                {
                                    "name": "pointsAgainst",
                                    "displayName": "Points Against",
                                    "shortDisplayName": "PA",
                                    "description": "Total Points Against",
                                    "abbreviation": "PA",
                                    "type": "pointsagainst",
                                    "value": 451.0,
                                    "displayValue": "451",
                                },
                                {
                                    "name": "pointsFor",
                                    "displayName": "Points For",
                                    "shortDisplayName": "PF",
                                    "description": "Total Points For",
                                    "abbreviation": "PF",
                                    "type": "pointsfor",
                                    "value": 356.0,
                                    "displayValue": "356",
                                },
                                {
                                    "name": "ties",
                                    "displayName": "Ties",
                                    "shortDisplayName": "T",
                                    "description": "Ties",
                                    "abbreviation": "T",
                                    "type": "ties",
                                    "value": 0.0,
                                    "displayValue": "0",
                                },
                                {
                                    "name": "winPercent",
                                    "displayName": "Win Percentage",
                                    "shortDisplayName": "PCT",
                                    "description": "Winning Percentage",
                                    "abbreviation": "PCT",
                                    "type": "winpercent",
                                    "value": 0.29411766,
                                    "displayValue": ".294",
                                },
                                {
                                    "name": "wins",
                                    "displayName": "Wins",
                                    "shortDisplayName": "W",
                                    "description": "Wins",
                                    "abbreviation": "W",
                                    "type": "wins",
                                    "value": 5.0,
                                    "displayValue": "5",
                                },
                                {
                                    "id": "0",
                                    "name": "overall",
                                    "abbreviation": "Any",
                                    "type": "total",
                                    "summary": "5-12",
                                    "displayValue": "5-12",
                                },
                            ],
                            "logo": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:58Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/wsh.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:58Z",
                                },
                            ],
                        },
                        {
                            "team": "New York",
                            "link": "https://www.espn.com/nfl/team/_/name/nyg/new-york-giants",
                            "id": "19",
                            "uid": "s:20~l:28~t:19",
                            "stats": [
                                {
                                    "name": "losses",
                                    "displayName": "Losses",
                                    "shortDisplayName": "L",
                                    "description": "Losses",
                                    "abbreviation": "L",
                                    "type": "losses",
                                    "value": 13.0,
                                    "displayValue": "13",
                                },
                                {
                                    "name": "pointsAgainst",
                                    "displayName": "Points Against",
                                    "shortDisplayName": "PA",
                                    "description": "Total Points Against",
                                    "abbreviation": "PA",
                                    "type": "pointsagainst",
                                    "value": 439.0,
                                    "displayValue": "439",
                                },
                                {
                                    "name": "pointsFor",
                                    "displayName": "Points For",
                                    "shortDisplayName": "PF",
                                    "description": "Total Points For",
                                    "abbreviation": "PF",
                                    "type": "pointsfor",
                                    "value": 381.0,
                                    "displayValue": "381",
                                },
                                {
                                    "name": "ties",
                                    "displayName": "Ties",
                                    "shortDisplayName": "T",
                                    "description": "Ties",
                                    "abbreviation": "T",
                                    "type": "ties",
                                    "value": 0.0,
                                    "displayValue": "0",
                                },
                                {
                                    "name": "winPercent",
                                    "displayName": "Win Percentage",
                                    "shortDisplayName": "PCT",
                                    "description": "Winning Percentage",
                                    "abbreviation": "PCT",
                                    "type": "winpercent",
                                    "value": 0.23529412,
                                    "displayValue": ".235",
                                },
                                {
                                    "name": "wins",
                                    "displayName": "Wins",
                                    "shortDisplayName": "W",
                                    "description": "Wins",
                                    "abbreviation": "W",
                                    "type": "wins",
                                    "value": 4.0,
                                    "displayValue": "4",
                                },
                                {
                                    "id": "0",
                                    "name": "overall",
                                    "abbreviation": "Any",
                                    "type": "total",
                                    "summary": "4-13",
                                    "displayValue": "4-13",
                                },
                            ],
                            "logo": [
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "default"],
                                    "lastUpdated": "2024-06-25T18:55Z",
                                },
                                {
                                    "href": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/scoreboard/nyg.png",
                                    "width": 500,
                                    "height": 500,
                                    "alt": "",
                                    "rel": ["full", "scoreboard", "dark"],
                                    "lastUpdated": "2024-06-25T18:59Z",
                                },
                            ],
                        },
                    ]
                },
                "header": "2025 NFC East Standings",
                "href": "https://www.espn.com/nfl/standings/_/group/1",
                "conferenceHeader": "National Football Conference",
                "divisionHeader": "NFC East",
            },
        ],
        "isSameConference": True,
    },
}
