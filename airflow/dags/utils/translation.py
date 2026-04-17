from models.clickhouse import PlayerGameStats, TeamGameStats
from dataclasses import asdict


class EspnTranslator:
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

    def to_player_stats(
        self, game_id: int, year: int, week: int, game_info: dict
    ) -> list[dict]:
        players = {}
        for team in game_info["boxscore"]["players"]:
            team_id = team["team"]["id"]
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
                        team_id=team_id,
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
                        team_id=team_id,
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
                        team_id=team_id,
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
                        team_id=team_id,
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

    def to_team_stats(self, game_id, year, week, game_info) -> list[dict]:
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
