import requests
import clickhouse_connect


clickhouse = clickhouse_connect.get_client(
    host="localhost", port=8123, username="default", password="default"
)


def main():
    page = 1
    limit = 50
    while page * limit < 20_000:
        print(f"Querying page {page} up to player {page * limit}")
        url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes?lang=en&region=us&page={page}&limit={limit}"
        response = requests.get(url).json()

        data = []
        for item in response["items"]:
            player_id = (
                item["$ref"]
                .strip(
                    "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes/"
                )
                .strip("?lang=en&region=us")
            )
            player_url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes/{player_id}?lang=en&region=us"
            player_response = requests.get(player_url).json()
            if player_response.get("active"):
                position = player_response["position"]["name"]
                height = player_response["height"]
                weight = player_response["weight"]
                if "draft" in player_response:
                    draft_year = player_response["draft"]["year"]
                    draft_round = player_response["draft"]["round"]
                    draft_selection = player_response["draft"]["selection"]

                name = player_response["displayName"]
                data.append([name, player_id, position, height, weight, draft_year, draft_round, draft_selection])
        print(data)
        clickhouse.insert(
            "mappings.players",
            data,
            column_names=[
                "name",
                "espn_id",
                "position",
                "height",
                "weight",
                "draft_year",
                "draft_round",
                "draft_selection",
            ],
        )
        page += 1


if __name__ == "__main__":
    main()
