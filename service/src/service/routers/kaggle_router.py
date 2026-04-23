import csv
from io import StringIO
from typing import Annotated

from clickhouse_connect.driver.client import Client
from common.db import get_clickhouse_client
from fastapi import APIRouter, Depends, Response

router = APIRouter()

ClickhouseClient = Annotated[Client, Depends(get_clickhouse_client)]


@router.get("/data", tags=["Kaggle"])
async def data(
    client: ClickhouseClient,
    start_year: int = 2025,
    end_year: int = 2025,
    limit: int = 0,
):
    query = f"SELECT * FROM gold.playergame WHERE season >= {start_year} and season <= {end_year}"
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
    query = f"SELECT * FROM gold.playergame WHERE season >= {start_year} and season <= {end_year}"
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
