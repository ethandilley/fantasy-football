from fastapi import FastAPI
import requests

app = FastAPI()


base_url = "https://sports.core.api.espn.com/v3/sports/football/leagues/nfl/"

@app.get("/get_calendars")
async def root():
    response = requests.get(base_url + "seasons")
    return response.json()
