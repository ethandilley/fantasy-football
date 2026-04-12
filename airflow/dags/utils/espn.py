import requests


class EspnClient:
    BASE_URL = "https://site.api.espn.com/apis/site/v2"
    CORE_URL = "https://sports.core.api.espn.com/v2"

    FOOTBALL_PATH = "sports/football"

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, url, params=None):
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_events(self, year: int, week: int):
        """
        Returns raw events list for a week
        """
        events_path = f"leagues/nfl/seasons/{year}/types/2/weeks/{week}/events"
        url = f"{self.CORE_URL}/{self.FOOTBALL_PATH}/{events_path}"
        return self._get(url)

    def get_event_ids(self, year: int, week: int):
        data = self.get_events(year, week)

        ids = []
        for item in data.get("items", []):
            ref = item.get("$ref", "")
            if "/events/" in ref:
                ids.append(ref.split("/events/")[1].split("?")[0])

        return ids

    def get_stats(self, event_id: str):
        summary_path = "nfl/summary"
        url = f"{self.BASE_URL}/{self.FOOTBALL_PATH}/{summary_path}"
        return self._get(url, params={"event": event_id})
