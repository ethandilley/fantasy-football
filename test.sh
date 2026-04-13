curl -X POST "http://localhost:8080/api/v2/dags/populate_player_game_stats/dagRuns" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${AIRFLOW_TOKEN}" \
     -d '{"conf": {"year": 2018, "week": 4}, "logical_date": "2026-04-12T12:00:00Z"}'

