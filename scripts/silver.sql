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
CREATE or replace TABLE silver.playergamestats
(
    player_id Int not null,
    name String not null,
    game_id Int not null,
    team_id Int not null,
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

-- adp table
CREATE OR REPLACE TABLE silver.adp
(
    id UUID DEFAULT generateUUIDv4(),
    source String NOT NULL,
    ffc_player_id Int NOT NULL,
    player_name String NOT NULL,
    position String,
    season Int NOT NULL,
    scoring_format String NOT NULL,
    teams Int NOT NULL,
    adp Float NOT NULL,
    times_drafted Int,
    high Int,
    low Int,
    stdev Float,
    total_drafts Int,
    start_date Date,
    end_date Date
)
ENGINE = ReplacingMergeTree()
ORDER BY (source, season, scoring_format, teams, ffc_player_id);

-- sportsbook markets table
CREATE OR REPLACE TABLE silver.markets
(
    id UUID DEFAULT generateUUIDv4(),
    event_key String NOT NULL,
    market_key String NOT NULL,
    market_type String NOT NULL,       -- POINT_SPREAD, POINT_TOTAL, PLAYER_RECEPTIONS
    segment String NOT NULL,            -- FULL_MATCH, FIRST_HALF, etc.
    player_id Nullable(Int),
    team_id Nullable(Int),
    last_found_at DateTime NOT NULL
)
ENGINE = ReplacingMergeTree()
ORDER BY (event_key, market_key);

-- sportsbook odds table
CREATE OR REPLACE TABLE silver.odds
(
    id UUID DEFAULT generateUUIDv4(),
    event_key String NOT NULL,
    market_key String NOT NULL,
    sportsbook String NOT NULL,         -- DRAFT_KINGS, FAN_DUEL
    market_type String NOT NULL,        -- POINT_SPREAD, PLAYER_RECEPTIONS
    segment String NOT NULL,
    participant_key String NOT NULL,
    participant_name String NOT NULL,
    -- for teams: SEA, NE
    -- for players: player name
    participant_type String NOT NULL,   -- TEAM / PLAYER
    outcome_type String NOT NULL,       -- WIN, OVER, UNDER
    line Float64,                       -- -3.5, 45.5, 72.5 yards
    decimal_odds Float64 NOT NULL,      -- 1.909091
    american_odds Int32,
    live Boolean NOT NULL,
    updated_at DateTime NOT NULL
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY
(
    event_key,
    market_key,
    sportsbook,
    participant_key,
    outcome_type
);

CREATE OR REPLACE TABLE silver.odds_events
(
    odds_event_key String NOT NULL,
    espn_game_id Int NOT NULL
)
ENGINE = ReplacingMergeTree()
ORDER BY odds_event_key;
