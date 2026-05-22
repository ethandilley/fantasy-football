from services.dataset import DatasetService
from repository.dataset import DatasetRepository
from fastapi import Depends
from common.db import get_clickhouse


def get_dataset_repository(db=Depends(get_clickhouse)) -> DatasetRepository:
    return DatasetRepository(db)


def get_dataset_service(
    repo: DatasetRepository = Depends(get_dataset_repository),
) -> DatasetService:
    return DatasetService(repo)
