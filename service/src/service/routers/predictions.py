from fastapi import APIRouter

router = APIRouter()

@router.get("/predictions/evaluate", tags=["Predictions"])
async def evaluate():
    print("evaluate")

@router.get("predictions/leaderboard", tags=["Predictions"])
async def leaderboard():
    print("leaderboard")

@router.get("/predictions/{id}", tags=["Predictions"])
async def player_stats(id: int):
    print(f"prediction {id}")
