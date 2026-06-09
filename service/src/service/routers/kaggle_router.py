import csv
from sklearn.metrics import r2_score
from io import BytesIO, StringIO
from typing import Annotated

import pandas as pd
from clickhouse_connect.driver.client import Client
from common.db import get_clickhouse_client
from fastapi import APIRouter, Depends, File, Response

router = APIRouter()

ClickhouseClient = Annotated[Client, Depends(get_clickhouse_client)]


@router.get("/datasets", tags=["Kaggle"])
async def datasets() -> list[str]:
    return ["playergames"]


@router.get("/datasets/{dataset_id}", tags=["Kaggle"])
async def dataset(dataset_id: str):
    datasets = {
        "playergame": {
            "id": "playergame",
            "description": "Per-player, per-game statistics with fantasy scoring.",
            "target_column": "fantasy_points",
            "min_season": 1999,
            "max_season": 2025,
        }
    }
    return datasets[dataset_id]


@router.get("/datasets/{dataset_id}/records", tags=["Kaggle"])
async def records(
    client: ClickhouseClient,
    dataset_id: str = "playergame",
    min_season: int = 1999,
    max_season: int = 2025,
    include_outcomes: bool = True,
    page: int = 1,
    page_size: int = 1000,
):
    pass


@router.get("/datasets/{dataset_id}/export", tags=["Kaggle"])
async def export(
    client: ClickhouseClient,
    dataset_id: str = "playergame",
    min_season: int = 1999,
    max_season: int = 2025,
    include_outcomes: bool = True,
):
    pass


@router.post("/competition/{dataset_id}/submit", tags=["Kaggle"])
async def submit(
    client: ClickhouseClient,
    file: Annotated[bytes, File()],
    dataset_id: str = "playergame",
):
    pass


@router.get("/competition/{dataset_id}/leaderboard")
async def get_leaderboard(
    dataset_id: str,
    limit: int = 100,
):
    pass
