from repository.dataset import DatasetRepository


class DatasetService:
    def __init__(self, repo: DatasetRepository):
        self.repo = repo

    def get_training(self, season: int, week: int, page: int, limit: int):
        result = self.repo.get_training(season, week, page, limit)
        columns = result.column_names
        rows = result.result_rows
        return [dict(zip(columns, row)) for row in rows]

    def get_testing(self, season: int, week: int, page: int, limit: int):
        result = self.repo.get_testing(season, week, page, limit)
        columns = result.column_names
        rows = result.result_rows
        return [dict(zip(columns, row)) for row in rows]
