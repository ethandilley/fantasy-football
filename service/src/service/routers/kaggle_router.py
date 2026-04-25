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


@router.get("/data", tags=["Kaggle"])
async def data(
    client: ClickhouseClient,
    start_year: int = 2025,
    end_year: int = 2025,
    limit: int = 0,
):
    query = f"SELECT * FROM gold.playergame final WHERE season >= {start_year} and season <= {end_year}"
    if limit != 0:
        query = query + f" limit {limit}"

    result = client.query(query)

    columns = result.column_names
    rows = result.result_rows

    data = [dict(zip(columns, row)) for row in rows]
    return data


@router.get("/download", tags=["Kaggle"])
async def download(
    client: ClickhouseClient,
    start_year: int = 2025,
    end_year: int = 2025,
    limit: int = 0,
):
    query = f"SELECT * FROM gold.playergame final WHERE season >= {start_year} and season <= {end_year}"
    if limit != 0:
        query = query + f" limit {limit}"

    result = client.query(query)

    columns = result.column_names
    rows = result.result_rows

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow(columns)
    writer.writerows(rows)

    csv_content = buffer.getvalue()
    buffer.close()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="playergame_{start_year}_{end_year}.csv"',
        },
    )


@router.get("/training", tags=["Kaggle"])
async def training(client: ClickhouseClient):
    query = "SELECT * FROM gold.playergame final WHERE season <= 2025"

    result = client.query(query)

    columns = result.column_names
    rows = result.result_rows

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow(columns)
    writer.writerows(rows)

    csv_content = buffer.getvalue()
    buffer.close()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="training.csv"',
        },
    )


@router.get("/prediction", tags=["Kaggle"])
async def prediction(client: ClickhouseClient):
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
        where season = 2025
    """

    result = client.query(query)

    columns = result.column_names
    rows = result.result_rows

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow(columns)
    writer.writerows(rows)

    csv_content = buffer.getvalue()
    buffer.close()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="prediction.csv"',
        },
    )


@router.post("/files")
async def create_file(client: ClickhouseClient, file: Annotated[bytes, File()]):
    predicted = pd.read_csv(BytesIO(file))[["id", "fantasy_points"]]
    query = """
        SELECT
            id,
            fantasy_points
        FROM gold.playergame final
        WHERE season = 2025
    """

    result = client.query(query)

    truth = pd.DataFrame(result.result_rows, columns=["id", "fantasy_points"])

    predicted["id"] = predicted["id"].astype(str)
    truth["id"] = truth["id"].astype(str)

    merged = truth.merge(predicted, on="id", suffixes=("_true", "_pred"))

    r2 = r2_score(merged["fantasy_points_true"], merged["fantasy_points_pred"])

    return {"file_size": len(file), "r2": r2}


