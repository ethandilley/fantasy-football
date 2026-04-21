from fastapi import APIRouter, Depends
from typing import Annotated
from common.db import get_clickhouse_client
from clickhouse_connect.driver.client import Client

router = APIRouter()

ClickhouseClient = Annotated[Client, Depends(get_clickhouse_client)]


@router.get("/data", tags=["Kaggle"])
async def data(client: ClickhouseClient, year: int = 1999):
    result = client.query(f"SELECT * FROM gold.playergame where season = {year}")
    
    columns = result.column_names
    rows = result.result_rows

    data = [dict(zip(columns, row)) for row in rows]
    return data
