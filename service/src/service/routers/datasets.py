from dependencies.dataset import get_dataset_service
from fastapi import APIRouter, Depends
from services.dataset import DatasetService
from fastapi.responses import StreamingResponse
import csv
import io

router = APIRouter(prefix="/datasets", tags=["Datasets"])


def _to_csv_response(data, filename: str) -> StreamingResponse:
    rows = data if isinstance(data, list) else data.get("items", [])

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/train")
async def train(
    service: DatasetService = Depends(get_dataset_service),
    season: int | None = None,
    week: int | None = None,
    page: int = 1,
    limit: int = 50,
    format: str = "json",
):
    data = service.get_training(season, week, page, limit)
    if format == "csv":
        return _to_csv_response(data, filename="train.csv")
    return data


@router.get("/test")
async def test(
    service: DatasetService = Depends(get_dataset_service),
    season: int | None = None,
    week: int | None = None,
    page: int = 1,
    limit: int = 50,
):
    data = service.get_testing(season, week, page, limit)
    if format == "csv":
        return _to_csv_response(data, filename="test.csv")
    return data
