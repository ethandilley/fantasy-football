CREATE DATABASE mappings;

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

drop table mappings.players;
