from fastapi import FastAPI
from routers import health_router
from routers import kaggle_router
from contextlib import asynccontextmanager
from clickhouse_connect import get_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.clickhouse_client = get_client(
        host="clickhouse", port=8123, username="default", password="default"
    )
    yield
    app.state.clickhouse_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
app.include_router(kaggle_router)
