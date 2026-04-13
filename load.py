import requests
from datetime import datetime, timezone
import os

airflow_token = os.environ.get("AIRFLOW_TOKEN")
# dag = "espn_stats"
dag = "populate_player_game_stats"
url = f"http://localhost:8080/api/v2/dags/{dag}/dagRuns"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {airflow_token}",
}

for year in range(2018, 2026):
    for week in range(1, 18):
        print(str(year) + ": " + str(week))

        logical_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        data = {"conf": {"year": year, "week": week}, "logical_date": logical_date}

        response = requests.post(url, headers=headers, json=data)
        print(response)
