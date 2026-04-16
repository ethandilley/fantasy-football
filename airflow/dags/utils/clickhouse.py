import clickhouse_connect


class ClickhouseClient:
    def __init__(
        self,
        host: str = "clickhouse",
        port: int = 8123,
        username: str = "default",
        password: str = "default",
    ):
        self.client = clickhouse_connect.get_client(
            host=host, port=port, username=username, password=password
        )

    def write_team_game_stats(self, data):
        print(data)
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
        self.client.insert("silver.teamgamestats", rows, column_names=columns)

    def write_player_game_stats(self, data):
        columns = [
            "player_id",
            "name",
            "game_id",
            "season",
            "week",
            "passing_attempts",
            "passing_completions",
            "passing_yards",
            "passing_tds",
            "interceptions",
            "rushing_attempts",
            "rushing_yards",
            "rushing_tds",
            "targets",
            "receptions",
            "receiving_yards",
            "receiving_tds",
            "fumbles",
            "fumbles_lost",
        ]
        print(data)
        rows = [[p[col] for col in columns] for p in data]
        print(rows)

        self.client.insert(
            "silver.playergamestats",
            rows,
            column_names=columns,
        )

    def write_players(self, data):
        columns = [
            "name",
            "espn_id",
            "position",
            "height",
            "weight",
            "age",
            "draft_year",
            "draft_round",
            "draft_selection",
            "status",
        ]
        print(data)
        rows = [[p[col] for col in columns] for p in data]
        print(rows)

        self.client.insert(
            "silver.players",
            rows,
            column_names=columns,
        )

    def write_teams(self, data):
        columns = [
            "name",
            "espn_id",
        ]
        print(data)
        rows = [[p[col] for col in columns] for p in data]
        print(rows)

        self.client.insert(
            "silver.teams",
            rows,
            column_names=columns,
        )

    def write_games(self, data):
        columns = [
            "espn_id",
            "slug",
            "season",
            "week",
            "home_team_id",
            "away_team_id",
            "home_score",
            "away_score",
            "game_date",
            "weather_condition",
            "temperature",
            "wind_speed",
        ]
        print(data)
        rows = [[data[col] for col in columns]]
        print(rows)

        self.client.insert(
            "silver.games",
            rows,
            column_names=columns,
        )
