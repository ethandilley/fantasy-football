from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from clickhouse_connect import get_client
from fastapi import FastAPI
from fastapi.responses import FileResponse
from routers import health_router, player_router, dataset_router, game_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.clickhouse_client = get_client(
        host="clickhouse", port=8123, username="default", password="default"
    )
    yield
    app.state.clickhouse_client.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(player_router)
app.include_router(dataset_router)
app.include_router(game_router)


@app.get("/")
def root():
    return FileResponse(Path(__file__).parent / "index.html")
