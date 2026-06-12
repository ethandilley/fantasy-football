from services.player import PlayerService
from repository.player import PlayerRepository
from fastapi import Depends
from common.db import get_clickhouse


def get_player_repository(db=Depends(get_clickhouse)) -> PlayerRepository:
    return PlayerRepository(db)


def get_player_service(
    repo: PlayerRepository = Depends(get_player_repository),
) -> PlayerService:
    return PlayerService(repo)
