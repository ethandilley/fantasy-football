-- create players table
CREATE TABLE mappings.players
(
    name String NOT NULL,
    espn_id Int NOT NULL,
    position String NOT NULL,
    height Int NOT NULL,
    weight Int NOT NULL,
    draft_year Int NOT NULL,
    draft_round Int NOT NULL,
    draft_selection Int NOT NULL
);

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
