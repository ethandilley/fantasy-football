from dependencies.game import get_game_service
from fastapi import APIRouter, Depends
from services.game import GameService

router = APIRouter(prefix="/games", tags=["Games"])


@router.get("")
async def games(
    service: GameService = Depends(get_game_service),
    season: int | None = None,
    week: int | None = None,
    page: int = 1,
    limit: int = 50,
):
    return service.get_games(season, week, page, limit)


@router.get("/{id}")
async def games_id(id: str, service: GameService = Depends(get_game_service)):
    return service.get_game(id)


@router.get("/{id}/players")
async def game_players(id: int):
    print(f"games {id} players")


@router.get("/{id}/stats")
async def game_stats(id: int):
    print(f"games {id} stats")
