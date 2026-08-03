from services.game import GameService
from repository.game import GameRepository
from fastapi import Depends
from common.db import get_clickhouse


def get_game_repository(db=Depends(get_clickhouse)) -> GameRepository:
    return GameRepository(db)


def get_game_service(
    repo: GameRepository = Depends(get_game_repository),
) -> GameService:
    return GameService(repo)
