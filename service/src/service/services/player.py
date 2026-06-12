from repository.player import PlayerRepository


class PlayerService:
    def __init__(self, repo: PlayerRepository):
        self.repo = repo

    def get_player(self, id: str):
        result = self.repo.get_player(id)
        columns = result.column_names
        rows = result.result_rows
        return [dict(zip(columns, row)) for row in rows]

    def get_players(
        self,
        draft_year: int | None,
        position: str | None,
        status: str | None,
        page: int,
        limit: int,
    ):
        result = self.repo.get_players(draft_year, position, status, page, limit)
        columns = result.column_names
        rows = result.result_rows
        return [dict(zip(columns, row)) for row in rows]

    def get_stats(self, id: str):
        result = self.repo.get_stats(id)
        columns = result.column_names
        rows = result.result_rows
        return [dict(zip(columns, row)) for row in rows]

