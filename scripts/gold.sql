--  playergame table
CREATE OR REPLACE TABLE gold.playergame
(
    id UUID DEFAULT GENERATEUUIDV4(),
    player_name STRING NOT NULL,
    player_id INT NOT NULL,
    position STRING,
    height NULLABLE(INT32),
    weight NULLABLE(INT32),
    age NULLABLE(INT32),
    draft_year NULLABLE(INT32),
    draft_round NULLABLE(INT32),
    draft_selection NULLABLE(INT32),
    status STRING NOT NULL,

    -- teams table
    team_name STRING NOT NULL,
    team_id INT NOT NULL,

    -- games table
    game_id INT NOT NULL,
    game_slug STRING NOT NULL,
    season INT NOT NULL,
    week INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    home_score INT NOT NULL,
    away_score INT NOT NULL,
    game_date STRING NOT NULL,
    weather_condition STRING,
    temperature INT,
    wind_speed INT,

    -- player table
    passing_attempts INT NOT NULL,
    passing_completions INT NOT NULL,
    passing_yards INT NOT NULL,
    passing_tds INT NOT NULL,
    interceptions INT NOT NULL,
    rushing_attempts INT NOT NULL,
    rushing_yards INT NOT NULL,
    rushing_tds INT NOT NULL,
    targets INT NOT NULL,
    receptions INT NOT NULL,
    receiving_yards INT NOT NULL,
    receiving_tds INT NOT NULL,
    fumbles INT NOT NULL,
    fumbles_lost INT NOT NULL,

    -- team game stats
    home_away STRING NOT NULL,
    first_downs INT NOT NULL,
    third_down_conversions INT NOT NULL,
    third_down_attempts INT NOT NULL,
    fourth_down_conversions INT NOT NULL,
    fourth_down_attempts INT NOT NULL,
    total_plays INT NOT NULL,
    total_yards INT NOT NULL,
    yards_per_play FLOAT NOT NULL,
    total_drives INT NOT NULL,
    net_passing_yards INT NOT NULL,
    team_passing_completions INT NOT NULL,
    team_passing_attempts INT NOT NULL,
    yards_per_pass FLOAT NOT NULL,
    interceptions_thrown INT NOT NULL,
    sacks INT NOT NULL,
    sack_yards_lost INT NOT NULL,
    team_rushing_yards INT NOT NULL,
    team_rushing_attempts INT NOT NULL,
    yards_per_rush FLOAT NOT NULL,
    red_zone_conversions INT NOT NULL,
    red_zone_attempts INT NOT NULL,
    turnovers INT NOT NULL,
    team_fumbles_lost INT NOT NULL,
    possession_time_seconds INT NOT NULL,

    -- calc
    fantasy_points FLOAT NOT NULL
)
ENGINE = REPLACINGMERGETREE()
ORDER BY (player_id, game_id);


-- features built on player game
CREATE OR REPLACE TABLE gold.playergame_features
(
    player_id INT NOT NULL,
    game_id INT NOT NULL,
    season INT NOT NULL,
    week INT NOT NULL,
    player_name STRING NOT NULL,
    position STRING,
    team_id INT NOT NULL,
    home_away STRING NOT NULL,
    weather_condition STRING,
    temperature NULLABLE(INT),
    wind_speed NULLABLE(INT),
    avg_fantasy_points_last3 NULLABLE(FLOAT),
    avg_fantasy_points_last5 NULLABLE(FLOAT),
    avg_passing_yards_last3 NULLABLE(FLOAT),
    avg_rushing_yards_last3 NULLABLE(FLOAT),
    avg_receiving_yards_last3 NULLABLE(FLOAT),
    avg_targets_last3 NULLABLE(FLOAT),
    opp_avg_passing_yards_allowed_last3 NULLABLE(FLOAT),
    opp_avg_rushing_yards_allowed_last3 NULLABLE(FLOAT),
    opp_avg_receiving_yards_allowed_last3 NULLABLE(FLOAT),
    games_played_this_season INT NOT NULL,
    fantasy_points_ppr FLOAT NOT NULL
)
ENGINE = REPLACINGMERGETREE()
ORDER BY (player_id, game_id)
