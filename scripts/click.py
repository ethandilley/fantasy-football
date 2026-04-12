import clickhouse_connect

client = clickhouse_connect.get_client(
    host="localhost", port=8123, user="default", password="default"
)
print(client.command("SELECT timezone()"))
