import requests

BASE_URL = "https://fantasyfootballcalculator.com/api/v1"


class FfcApiError(Exception):
    """Raised on network/HTTP failures - safe to retry."""

    pass


class FfcNoDataError(FfcApiError):
    """Raised when FFC has no ADP data for the requested combo - not retryable."""

    pass


class FfcClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    def _get(self, path: str, params: dict | None = None) -> dict:
        try:
            response = requests.get(f"{self.base_url}{path}", params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise FfcApiError(f"FFC request failed: {e}") from e

        data = response.json()
        if isinstance(data, dict) and data.get("status") == "Error":
            raise FfcNoDataError(data.get("errors", "Unknown FFC error"))
        return data

    def get_adp(self, scoring_format: str, teams: int, year: int) -> dict:
        return self._get(
            f"/adp/{scoring_format}", params={"teams": teams, "year": year}
        )
