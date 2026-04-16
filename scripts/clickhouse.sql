-- players table
CREATE OR REPLACE TABLE silver.players
(
    id UUID DEFAULT generateUUIDv4(),
    name String NOT NULL,
    espn_id Int NOT NULL,
    position String,
    height Nullable(Int32),
    weight Nullable(Int32),
    age Nullable(Int32),
    draft_year Nullable(Int32),
    draft_round Nullable(Int32),
    draft_selection Nullable(Int32),
    status String NOT NULL
)
ENGINE = ReplacingMergeTree()
ORDER BY (espn_id);

-- teams table
CREATE or replace TABLE silver.teams
(
    id UUID DEFAULT generateUUIDv4(),
    name String NOT NULL,
    espn_id Int NOT NULL
)
ENGINE = ReplacingMergeTree()
ORDER BY (espn_id);

-- games table
CREATE or replace TABLE silver.games
(
    id UUID DEFAULT generateUUIDv4(),
    espn_id Int NOT NULL,
    slug String NOT NULL,
    season Int NOT NULL,
    week Int NOT NULL,
    home_team_id Int NOT NULL,
    away_team_id Int NOT NULL,
    home_score Int NOT NULL,
    away_score Int NOT NULL,
    game_date String NOT NULL,
    weather_condition String,
    temperature Int,
    wind_speed Int
)
ENGINE = ReplacingMergeTree()
ORDER BY (espn_id);


-- create playergamestats table (huge table)
CREATE TABLE silver.playergamestats
(
    player_id Int not null,
    name String not null,
    game_id Int not null,
    season Int not null,
    week Int not null,
    passing_attempts int not null,
    passing_completions int not null,
    passing_yards int not null,
    passing_tds int not null,
    interceptions int not null,
    rushing_attempts int not null,
    rushing_yards int not null,
    rushing_tds int not null,
    targets int not null,
    receptions int not null,
    receiving_yards int not null,
    receiving_tds int not null,
    fumbles int not null,
    fumbles_lost int not null
)
ENGINE = ReplacingMergeTree()
ORDER BY (player_id, game_id);

CREATE TABLE silver.teamgamestats
(
    team_id         Int  NOT NULL,
    name String NOT NULL,
    game_id         Int  NOT NULL,
    season          Int  NOT NULL,
    week            Int  NOT NULL,
    home_away       String NOT NULL,
    first_downs                Int NOT NULL,
    third_down_conversions     Int NOT NULL,
    third_down_attempts        Int NOT NULL,
    fourth_down_conversions    Int NOT NULL,
    fourth_down_attempts       Int NOT NULL,
    total_plays                Int NOT NULL,
    total_yards                Int NOT NULL,
    yards_per_play             Float NOT NULL,
    total_drives               Int NOT NULL,
    net_passing_yards          Int NOT NULL,
    passing_completions        Int NOT NULL,
    passing_attempts           Int NOT NULL,
    yards_per_pass             Float NOT NULL,
    interceptions_thrown       Int NOT NULL,
    sacks                      Int NOT NULL,
    sack_yards_lost            Int NOT NULL,
    rushing_yards              Int NOT NULL,
    rushing_attempts           Int NOT NULL,
    yards_per_rush             Float NOT NULL,
    red_zone_conversions       Int NOT NULL,
    red_zone_attempts          Int NOT NULL,
    turnovers                  Int NOT NULL,
    fumbles_lost               Int NOT NULL,
    possession_time_seconds    Int NOT NULL
)
ENGINE = ReplacingMergeTree()
ORDER BY (team_id, game_id);


