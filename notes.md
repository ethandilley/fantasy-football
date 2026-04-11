# Bronze
bronze/
  espn/
    boxscores/
      v1/
        year=2025/
          week=01/
            game_id=401547353/
              2026-04-11T18:05:12Z.json
              2026-04-11T18:10:44Z.json

1. events (games list per week)
url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/types/2/weeks/{week}/events"
game_ids

2. Boxscore (player stats per game)
url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}"
player stats
team stats
scoring plays

# Silver
tables
players
    - player_id (internal ID)
    - espn_id
    - name
    - position (QB, RB, WR, TE, K, DST)
    - team_id
    - active_status
    - rookie_year
    - height/weight
    - birthdate
    - current_team

teams:
    - team_id
    - season
    - team_name
    - division
    - conference

games
    - game_id
    - season
    - week
    - home_team_id
    - away_team_id
    - date
    - weather

player_game_stats
Identity
    - player_id
    - game_id
    - season
    - week
    - team_id
    - opponent_team_id

stats
    - passing_attempts
    - passing_completions
    - passing_yards
    - passing_tds
    - interceptions
    - rushing_attempts
    - rushing_yards
    - rushing_tds
    - targets
    - receptions
    - receiving_yards
    - receiving_tds
    - fumbles
    - fumbles_lost
    - Participation / usage

usage
    - snaps
    - snap_share
    - red_zone_touches

results
    - home_away_flag
    - game_result (W/L)

team_game_stats

Fields:
team_id
game_id
season
week

Offense:
total_yards
passing_yards
rushing_yards
points_scored
turnovers

Defense:
points_allowed
yards_allowed
sacks
interceptions
