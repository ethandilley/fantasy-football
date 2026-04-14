import requests
from dataclasses import asdict
from models.clickhouse import PlayerGameStats, TeamGameStats


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

    @staticmethod
    def _parse_fraction(value: str) -> tuple[int, int]:
        """Parse 'made-attempts' or 'made/attempts' strings into (made, attempts)."""
        for sep in ["-", "/"]:
            if sep in value:
                a, b = value.split(sep)
                return int(a), int(b)
        return 0, 0

    @staticmethod
    def _get_stat(statistics: list, name: str) -> dict | None:
        """Look up a stat entry by name from the statistics list."""
        for s in statistics:
            if s["name"] == name:
                return s
        return None

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

    def get_players(self, page: int = 1, limit: int = 1):
        athlete_path = "leagues/nfl/athletes"
        url = f"{self.CORE_URL}/{self.FOOTBALL_PATH}/{athlete_path}"
        return self._get(url, params={"limit": limit, "page": page})

    def get_player_count(self):
        data = self.get_players()
        return data["count"]

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

    def build_teams(self, game_id, year, week, game_info):
        teams = []
        for team in game_info["boxscore"]["teams"]:
            team_id = int(team["team"]["id"])
            home_away = team["homeAway"]
            stats = team["statistics"]

            third_conv, third_att = self._parse_fraction(
                self._get_stat(stats, "thirdDownEff")["displayValue"]
            )
            fourth_conv, fourth_att = self._parse_fraction(
                self._get_stat(stats, "fourthDownEff")["displayValue"]
            )
            pass_comp, pass_att = self._parse_fraction(
                self._get_stat(stats, "completionAttempts")["displayValue"]
            )
            sacks, sack_yards = self._parse_fraction(
                self._get_stat(stats, "sacksYardsLost")["displayValue"]
            )
            rz_conv, rz_att = self._parse_fraction(
                self._get_stat(stats, "redZoneAttempts")["displayValue"]
            )

            statline = TeamGameStats(
                team_id=team_id,
                name=team["team"]["displayName"],
                game_id=game_id,
                season=year,
                week=week,
                home_away=home_away,
                first_downs=int(self._get_stat(stats, "firstDowns")["displayValue"]),
                third_down_conversions=third_conv,
                third_down_attempts=third_att,
                fourth_down_conversions=fourth_conv,
                fourth_down_attempts=fourth_att,
                total_plays=int(
                    self._get_stat(stats, "totalOffensivePlays")["displayValue"]
                ),
                total_yards=int(self._get_stat(stats, "totalYards")["displayValue"]),
                yards_per_play=float(
                    self._get_stat(stats, "yardsPerPlay")["displayValue"]
                ),
                total_drives=int(self._get_stat(stats, "totalDrives")["displayValue"]),
                net_passing_yards=int(
                    self._get_stat(stats, "netPassingYards")["displayValue"]
                ),
                passing_completions=pass_comp,
                passing_attempts=pass_att,
                yards_per_pass=float(
                    self._get_stat(stats, "yardsPerPass")["displayValue"]
                ),
                interceptions_thrown=int(
                    self._get_stat(stats, "interceptions")["displayValue"]
                ),
                sacks=sacks,
                sack_yards_lost=sack_yards,
                rushing_yards=int(
                    self._get_stat(stats, "rushingYards")["displayValue"]
                ),
                rushing_attempts=int(
                    self._get_stat(stats, "rushingAttempts")["displayValue"]
                ),
                yards_per_rush=float(
                    self._get_stat(stats, "yardsPerRushAttempt")["displayValue"]
                ),
                red_zone_conversions=rz_conv,
                red_zone_attempts=rz_att,
                turnovers=int(self._get_stat(stats, "turnovers")["displayValue"]),
                fumbles_lost=int(self._get_stat(stats, "fumblesLost")["displayValue"]),
                possession_time_seconds=int(
                    self._get_stat(stats, "possessionTime")["value"]
                ),
            )
            teams.append(statline)
        return [asdict(p) for p in teams]

batch_size = 75
e = EspnClient()
player_count = e.get_player_count()
pages = player_count // batch_size
parameters = [(i, batch_size) for i in range(pages + 1)]
print(parameters)

params = {}

