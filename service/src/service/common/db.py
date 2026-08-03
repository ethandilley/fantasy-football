import clickhouse_connect
from contextlib import contextmanager

_client = None

def get_clickhouse():
    global _client
    if _client is None:
        try:
            _client = clickhouse_connect.get_client(
                host="clickhouse", port=8123, username="default", password="default"
            )
        except Exception as e:
            raise RuntimeError(f"Could not connect to ClickHouse: {e}") from e
    return _client
