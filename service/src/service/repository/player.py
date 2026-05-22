from clickhouse_connect.driver.client import Client


class PlayerRepository:
    def __init__(self, db: Client):
        self.db = db

    def get_player(self, id: str):
        query = f"select * from silver.players final where id = '{id}'"
        result = self.db.query(query)
        return result

    def get_players(
        self,
        draft_year: int | None,
        position: str | None,
        status: str | None,
        page: int,
        limit: int,
    ):
        query = "select * from silver.players final where 1=1"
        if draft_year:
            query = query + f" and draft_year = {draft_year}"
        if position:
            query = query + f" and position = '{position}'"
        if status:
            query = query + f" and status = '{status}'"
        query = query + f" limit {limit} offset {(page - 1) * limit}"

        result = self.db.query(query)
        return result

    def get_stats(self, id: str):
        query = f"select * from gold.playergame final where id = '{id}'"
        result = self.db.query(query)
        return result
