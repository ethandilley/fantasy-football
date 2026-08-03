from clickhouse_connect.driver.client import Client


class GameRepository:
    def __init__(self, db: Client):
        self.db = db

    def get_game(self, id: str):
        query = f"select * from silver.games final where id = '{id}'"
        result = self.db.query(query)
        return result

    def get_games(
        self,
        season: int | None,
        week: int | None,
        page: int,
        limit: int,
    ):
        query = "select * from silver.games final where 1=1"
        if season:
            query = query + f" and season = {season}"
        if week:
            query = query + f" and week = {week}"
        query = query + f" limit {limit} offset {(page - 1) * limit}"

        result = self.db.query(query)
        return result
