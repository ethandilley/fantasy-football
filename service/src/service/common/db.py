from fastapi import Request


def get_clickhouse_client(request: Request):
    return request.app.state.clickhouse_client
