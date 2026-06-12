from clickhouse_connect.driver.client import Client


class DatasetRepository:
    def __init__(self, db: Client):
        self.db = db

    def get_training(self, season: int, week: int, page: int, limit: int):
        query = "select * from gold.playergame final where 1=1"
        if season:
            query = query + f" and season = {season}"
        if week:
            query = query + f" and week = {week}"
        query = query + f" limit {limit} offset {(page - 1) * limit}"

        result = self.db.query(query)
        return result

    def get_testing(self, season: int, week: int, page: int, limit: int):
        query = """
        select
            id,
            player_name,
            player_id,
            position,
            height,
            weight,
            age,
            draft_year,
            draft_round,
            draft_selection,
            status,
            team_name,
            team_id,
            game_id,
            game_slug,
            season,
            week,
            home_team_id,
            away_team_id,
            game_date,
            home_away
        from gold.playergame final
        where 1=1
        """
        if season:
            query = query + f" and season = {season}"
        if week:
            query = query + f" and week = {week}"
        query = query + f" limit {limit} offset {(page - 1) * limit}"

        result = self.db.query(query)
        return result
