import requests
from dataclasses import asdict
from models.clickhouse import PlayerGameStats


class EspnClient:
    BASE_URL = "https://site.api.espn.com/apis/site/v2"
    CORE_URL = "https://sports.core.api.espn.com/v2"

    FOOTBALL_PATH = "sports/football"

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, url, params=None):
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_events(self, year: int, week: int):
        """
        Returns raw events list for a week
        """
        events_path = f"leagues/nfl/seasons/{year}/types/2/weeks/{week}/events"
        url = f"{self.CORE_URL}/{self.FOOTBALL_PATH}/{events_path}"
        return self._get(url)

    def get_event_ids(self, year: int, week: int):
        data = self.get_events(year, week)

        ids = []
        for item in data.get("items", []):
            ref = item.get("$ref", "")
            if "/events/" in ref:
                ids.append(ref.split("/events/")[1].split("?")[0])

        return ids

    def get_stats(self, event_id: str):
        summary_path = "nfl/summary"
        url = f"{self.BASE_URL}/{self.FOOTBALL_PATH}/{summary_path}"
        return self._get(url, params={"event": event_id})

    def build_players(self, game_id: int, year: int, week: int, game_info: dict):
        players = {}
        for team in game_info["boxscore"]["players"]:
            passing_stats = team["statistics"][0]
            rushing_stats = team["statistics"][1]
            receiving_stats = team["statistics"][2]
            fumble_stats = team["statistics"][3]

            # parse passing
            for athlete in passing_stats["athletes"]:
                player_id = int(athlete["athlete"]["id"])
                player = athlete["athlete"]["displayName"]
                stats = athlete["stats"]
                completions, attempts = stats[0].split("/")
                yards = stats[1]
                touchdowns = stats[3]
                interceptions = stats[4]

                statline = players.get(
                    player_id,
                    PlayerGameStats(
                        player_id=player_id,
                        name=player,
                        game_id=game_id,
                        season=year,
                        week=week,
                    ),
                )
                statline.passing_attempts = int(attempts)
                statline.passing_completions = int(completions)
                statline.passing_yards = int(yards)
                statline.passing_tds = int(touchdowns)
                statline.interceptions = int(interceptions)
                players[player_id] = statline

            # parse rushing
            for athlete in rushing_stats["athletes"]:
                player_id = int(athlete["athlete"]["id"])
                player = athlete["athlete"]["displayName"]
                stats = athlete["stats"]
                attempts = stats[0]
                yards = stats[1]
                tds = stats[3]

                statline = players.get(
                    player_id,
                    PlayerGameStats(
                        player_id=player_id,
                        name=player,
                        game_id=game_id,
                        season=year,
                        week=week,
                    ),
                )
                statline.rushing_attempts = int(attempts)
                statline.rushing_yards = int(yards)
                statline.rushing_tds = int(tds)
                players[player_id] = statline

            for athlete in receiving_stats["athletes"]:
                player_id = int(athlete["athlete"]["id"])
                player = athlete["athlete"]["displayName"]
                stats = athlete["stats"]
                targets = stats[5]
                receptions = stats[0]
                yards = stats[1]
                touchdowns = stats[3]

                statline = players.get(
                    player_id,
                    PlayerGameStats(
                        player_id=player_id,
                        name=player,
                        game_id=game_id,
                        season=year,
                        week=week,
                    ),
                )
                statline.targets = int(targets)
                statline.receptions = int(receptions)
                statline.receiving_yards = int(yards)
                statline.receiving_tds = int(touchdowns)
                players[player_id] = statline

            for athlete in fumble_stats["athletes"]:
                player_id = int(athlete["athlete"]["id"])
                player = athlete["athlete"]["displayName"]
                stats = athlete["stats"]
                fumbles = stats[0]
                lost = stats[1]

                statline = players.get(
                    player_id,
                    PlayerGameStats(
                        player_id=player_id,
                        name=player,
                        game_id=game_id,
                        season=year,
                        week=week,
                    ),
                )
                statline.fumbles = int(fumbles)
                statline.fumbles_lost = int(lost)
                players[player_id] = statline
        return [asdict(p) for p in players.values()]
