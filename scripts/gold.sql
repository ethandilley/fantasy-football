--  playergame table
CREATE OR REPLACE TABLE gold.playergame
(
    id UUID DEFAULT generateUUIDv4(),
    player_name String NOT NULL,
    player_id Int NOT NULL,
    position String,
    height Nullable(Int32),
    weight Nullable(Int32),
    age Nullable(Int32),
    draft_year Nullable(Int32),
    draft_round Nullable(Int32),
    draft_selection Nullable(Int32),
    status String NOT NULL,
    -- teams table
    team_name String NOT NULL,
    team_id Int NOT NULL,
    -- games table
    game_id Int NOT NULL,
    game_slug String NOT NULL,
    season Int NOT NULL,
    week Int NOT NULL,
    home_team_id Int NOT NULL,
    away_team_id Int NOT NULL,
    home_score Int NOT NULL,
    away_score Int NOT NULL,
    game_date String NOT NULL,
    weather_condition String,
    temperature Int,
    wind_speed Int,
    -- player table
    passing_attempts Int NOT NULL,
    passing_completions Int NOT NULL,
    passing_yards Int NOT NULL,
    passing_tds Int NOT NULL,
    interceptions Int NOT NULL,
    rushing_attempts Int NOT NULL,
    rushing_yards Int NOT NULL,
    rushing_tds Int NOT NULL,
    targets Int NOT NULL,
    receptions Int NOT NULL,
    receiving_yards Int NOT NULL,
    receiving_tds Int NOT NULL,
    fumbles Int NOT NULL,
    fumbles_lost Int NOT NULL,
    -- team game stats
    home_away String NOT NULL,
    first_downs Int NOT NULL,
    third_down_conversions Int NOT NULL,
    third_down_attempts Int NOT NULL,
    fourth_down_conversions Int NOT NULL,
    fourth_down_attempts Int NOT NULL,
    total_plays Int NOT NULL,
    total_yards Int NOT NULL,
    yards_per_play Float NOT NULL,
    total_drives Int NOT NULL,
    net_passing_yards Int NOT NULL,
    team_passing_completions Int NOT NULL,
    team_passing_attempts Int NOT NULL,
    yards_per_pass Float NOT NULL,
    interceptions_thrown Int NOT NULL,
    sacks Int NOT NULL,
    sack_yards_lost Int NOT NULL,
    team_rushing_yards Int NOT NULL,
    team_rushing_attempts Int NOT NULL,
    yards_per_rush Float NOT NULL,
    red_zone_conversions Int NOT NULL,
    red_zone_attempts Int NOT NULL,
    turnovers Int NOT NULL,
    team_fumbles_lost Int NOT NULL,
    possession_time_seconds Int NOT NULL,
    -- calc
    fantasy_points Float NOT NULL
)
ENGINE = ReplacingMergeTree()
ORDER BY (player_id, game_id);


-- features built on player game
CREATE OR REPLACE TABLE gold.playergame_features
(
    player_id Int NOT NULL,
    game_id Int NOT NULL,
    season Int NOT NULL,
    week Int NOT NULL,
    player_name String NOT NULL,
    position String,
    team_id Int NOT NULL,
    home_away String NOT NULL,
    weather_condition String,
    temperature Nullable(Int),
    wind_speed Nullable(Int),
    avg_fantasy_points_last3 Nullable(Float),
    avg_fantasy_points_last5 Nullable(Float),
    avg_passing_yards_last3 Nullable(Float),
    avg_rushing_yards_last3 Nullable(Float),
    avg_receiving_yards_last3 Nullable(Float),
    avg_targets_last3 Nullable(Float),
    opp_avg_passing_yards_allowed_last3 Nullable(Float),
    opp_avg_rushing_yards_allowed_last3 Nullable(Float),
    opp_avg_receiving_yards_allowed_last3 Nullable(Float),
    games_played_this_season Int NOT NULL,
    fantasy_points_ppr Float NOT NULL
)
ENGINE = ReplacingMergeTree()
ORDER BY (player_id, game_id)
