from dependencies.player import get_player_service
from services.player import PlayerService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("")
async def players(
    service: PlayerService = Depends(get_player_service),
    draft_year: int | None = None,
    position: str | None = None,
    status: str | None = None,
    page: int = 1,
    limit: int = 50,
):
    return service.get_players(draft_year, position, status, page, limit)


@router.get("/{id}")
async def id(id: str, service: PlayerService = Depends(get_player_service)):
    return service.get_player(id)


@router.get("/{id}/stats")
async def stats(
    id: str,
    service: PlayerService = Depends(get_player_service),
):
    return service.get_stats(id)
