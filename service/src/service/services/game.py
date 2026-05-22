from repository.game import GameRepository


class GameService:
    def __init__(self, repo: GameRepository):
        self.repo = repo

    def get_game(self, id: str):
        result = self.repo.get_game(id)
        columns = result.column_names
        rows = result.result_rows
        return [dict(zip(columns, row)) for row in rows]

    def get_games(
        self,
        season: int | None,
        week: int | None,
        page: int,
        limit: int,
    ):
        result = self.repo.get_games(season, week, page, limit)
        columns = result.column_names
        rows = result.result_rows
        return [dict(zip(columns, row)) for row in rows]
