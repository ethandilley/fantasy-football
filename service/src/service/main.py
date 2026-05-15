from contextlib import asynccontextmanager
from pathlib import Path

from clickhouse_connect import get_client
from fastapi import FastAPI
from fastapi.responses import FileResponse
from routers import health_router, kaggle_router


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

@app.get("/")
def root():
    return FileResponse(Path(__file__).parent / "index.html")
