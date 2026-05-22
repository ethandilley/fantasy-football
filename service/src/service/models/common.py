from pydantic import BaseModel


class PaginationRequest(BaseModel):
    page: int = 1
    limit: int = 50
