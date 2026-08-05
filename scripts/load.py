import requests
import time
from datetime import datetime, timezone
import os

airflow_token = os.environ.get("AIRFLOW_TOKEN")
dags = [
    # ("bronze_games", 1),
    # ("silver_team_games", 5),
    # ("silver_player_games", 5),
    ("silver_games", 1),
    # ("gold_player_games", 1),
    # ("bronze_adp_ffc", 1),
    # ("silver_adp", 1),
]

BASE_URL = "http://localhost:8080/api/v2"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {airflow_token}",
}

MAX_IN_FLIGHT = 5  # running + queued


def get_in_flight(dag):
    url = f"{BASE_URL}/dags/{dag}/dagRuns"
    r = requests.get(url, headers=headers)
    runs = r.json().get("dag_runs", [])

    return len([run for run in runs if run["state"] in ["running", "queued"]])


for dag, buffer in dags:
    # for year in range(2010, 2027):
    for year in range(2001, 2026):
        for week in range(1, 19):
            logical_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # print(f"Triggering {year}")
            # data = {"conf": {"year": year}, "logical_date": logical_date}

            print(f"Triggering {year} week {week}")
            data = {"conf": {"year": year, "week": week}, "logical_date": logical_date}

            url = f"{BASE_URL}/dags/{dag}/dagRuns"
            response = requests.post(url, headers=headers, json=data)

            print(response.status_code)
            print(response.json())

            time.sleep(buffer)
