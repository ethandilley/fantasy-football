from dependencies.dataset import get_dataset_service
from fastapi import APIRouter, Depends
from services.dataset import DatasetService

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.get("/train")
async def train(
    service: DatasetService = Depends(get_dataset_service),
    season: int | None = None,
    week: int | None = None,
    page: int = 1,
    limit: int = 50,
):
    return service.get_training(season, week, page, limit)


@router.get("/test")
async def test(
    service: DatasetService = Depends(get_dataset_service),
    season: int | None = None,
    week: int | None = None,
    page: int = 1,
    limit: int = 50,
):
    return service.get_testing(season, week, page, limit)
