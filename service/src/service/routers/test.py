from sklearn.metrics import r2_score
from clickhouse_connect import get_client

import pandas as pd

predicted = pd.read_csv("output.csv")[["id", "fantasy_points"]]
query = """
    SELECT
        id,
        fantasy_points
    FROM gold.playergame final
    WHERE season = 2025
"""


client = get_client(host="localhost", port=8123, username="default", password="default")

result = client.query(query)

truth = pd.DataFrame(result.result_rows, columns=["id", "fantasy_points"])
import uuid

predicted["id"] = predicted["id"].astype(str)
truth["id"] = truth["id"].astype(str)
print("truth rows:", len(truth))
print(truth.head())

print(predicted.head())
print(predicted["id"].head().tolist())
print(truth["id"].head().tolist()[:5])

merged = truth.merge(predicted, on="id", suffixes=("_true", "_pred"))
print(merged)

r2 = r2_score(merged["fantasy_points_true"], merged["fantasy_points_pred"])
