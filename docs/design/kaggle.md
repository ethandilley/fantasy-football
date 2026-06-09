# Kaggle

To make a fully functioning kaggle website I need to have the ability to

1. provide training and testing data (both exported and json, perhaps also metadata endpoint)
2. Evaluate model scores (perhaps larger submission with ui and words for thesis)
3. show a leaderboard

To do this I will support 3 endpoints

| Method | Endpoint                                 | Description                                           |
| ------ | ---------------------------------------- | ----------------------------------------------------- |
| `GET`  | `/v1/datasets`                           | available datasets                               |
| `GET`  | `/v1/datasets/{dataset_id}`              | dataset metadata and column schema           |
| `GET`  | `/v1/datasets/{dataset_id}/records`      | Retrieve paginated rows in json|
| `GET`  | `/v1/datasets/{dataset_id}/export`       | Streaming file download|
| `POST` | `/v1/competitions/{comp_id}/submit` | Score a prediction file|
| `GET`  | `/v1/competitions/{comp_id}/leaderboard` | Retrieve ranked submissions|

