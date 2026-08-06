# utils/sportsbook.py
import os
import requests

RAPIDAPI_HOST = "sportsbook-api2.p.rapidapi.com"
# RAPIDAPI_KEY = os.environ["SPORTSBOOK_RAPIDAPI_KEY"]
RAPIDAPI_KEY = "e60218d430msh5d37025eff76a38p115adfjsn46ea6feccf0c"
BASE_URL = f"https://{RAPIDAPI_HOST}"

NFL_COMPETITION_KEY = "Q63E-wddv-ddp4"

# NFL competitionInstanceKey by season start year, from GET /v0/competitions/?includeInstances=true
NFL_COMPETITION_INSTANCE_KEYS = {
    2021: "5wNw-wddv-vw4y",  # 2021-22 National Football League
    2022: "nviw-wgup-FaOV",  # 2022-23
    2023: "41hk-xcnv-JDqS",  # 2023-24
    2024: "fSfn-ybxv-3XVi",  # 2024-25
    2025: "k0qU-zcrx-Fger",  # 2025-26
    2026: "lgB4-Acxf-PBzJ",  # 2026-27 (current)
}


class SportsbookApiError(Exception):
    pass


class SportsbookClient:
    def __init__(self):
        self.headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY,
        }

    def get_events(self, year: int) -> dict:
        instance_key = NFL_COMPETITION_INSTANCE_KEYS.get(year)
        if instance_key is None:
            raise SportsbookApiError(f"No NFL competitionInstanceKey mapped for year={year}")

        # TODO: unconfirmed whether competitionInstanceKey filters historical
        # seasons on this endpoint, or if events are scoped some other way.
        # Verify against Swagger / a live call before relying on this for
        # years other than the current season.
        resp = requests.get(
            f"{BASE_URL}/v0/competitions/{NFL_COMPETITION_KEY}/events",
            headers=self.headers,
            params={"competitionInstanceKey": instance_key},
        )
        if not resp.ok:
            raise SportsbookApiError(f"get_events failed for year={year}: {resp.status_code} {resp.text}")
        return resp.json()

    def get_market_keys(self, events_response: dict) -> list[str]:
        return [
            market["key"]
            for event in events_response.get("events", [])
            for market in event.get("markets", [])
        ]

    def get_market_outcomes_latest(self, market_key: str) -> dict:
        resp = requests.get(
            f"{BASE_URL}/v0/markets/{market_key}/outcomes/latest",
            headers=self.headers,
        )
        if not resp.ok:
            raise SportsbookApiError(f"get_market_outcomes_latest failed for {market_key}: {resp.status_code} {resp.text}")
        return resp.json()
