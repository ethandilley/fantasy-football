from dags.utils.sportsbook import SportsbookClient
import requests

headers = {
    "x-rapidapi-host": "sportsbook-api2.p.rapidapi.com",
    "x-rapidapi-key": "41fba9696cmshd849afda196e89bp1b6a38jsn4d86f73614c1",
}
resp = requests.get(
    "https://sportsbook-api2.p.rapidapi.com/v1/competitions/NFL/events",
    headers=headers,
    params={
        "startTimeFrom": "2026-09-01T00:00:00.000Z",
        "startTimeTo": "2027-03-01T00:00:00.000Z",
    },
)
print(resp.text)
