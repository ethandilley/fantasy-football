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
