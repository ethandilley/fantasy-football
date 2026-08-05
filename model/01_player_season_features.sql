-- =====================================================================
-- Player-Season Feature Table
-- Rolls gold.playergame (player x game grain) up to player x season grain
-- for use as model training data (and as the feature source for
-- projecting the upcoming season from the most recent completed one).
-- =====================================================================

WITH ranked AS (
    -- FINAL collapses ReplacingMergeTree duplicate rows down to the latest
    -- version per (player_id, game_id) — without it, unmerged duplicate
    -- loads inflate every downstream sum/count.
    SELECT
        *,
        row_number() OVER (
            PARTITION BY player_id, season ORDER BY week DESC
        ) AS games_from_end
    FROM gold.playergame FINAL
)
SELECT
    player_id,
    argMax(player_name, game_date)      AS player_name,
    argMax(position, game_date)         AS position,
    season,

    -- static-ish attributes: take the latest value seen in the season
    argMax(height, game_date)           AS height,
    argMax(weight, game_date)           AS weight,
    argMax(age, game_date)              AS age,
    argMax(draft_year, game_date)       AS draft_year,
    argMax(draft_round, game_date)      AS draft_round,
    argMax(draft_selection, game_date)  AS draft_selection,
    argMax(status, game_date)           AS status,
    argMax(team_name, game_date)        AS team_name,
    argMax(team_id, game_date)          AS team_id,

    -- availability
    count()                             AS games_played,
    max(week)                           AS last_week_played,

    -- fantasy output
    sum(fantasy_points)                 AS total_fantasy_points,
    avg(fantasy_points)                 AS ppg,
    stddevPop(fantasy_points)           AS ppg_stddev,

    -- passing volume + efficiency
    sum(passing_attempts)               AS pass_att,
    sum(passing_completions)            AS pass_cmp,
    sum(passing_yards)                  AS pass_yds,
    sum(passing_tds)                    AS pass_td,
    sum(interceptions)                  AS pass_int,
    if(sum(passing_attempts) > 0, sum(passing_yards) / sum(passing_attempts), NULL)   AS yds_per_att,
    if(sum(passing_attempts) > 0, sum(passing_completions) / sum(passing_attempts), NULL) AS completion_pct,
    if(sum(passing_attempts) > 0, sum(passing_tds) / sum(passing_attempts), NULL)     AS pass_td_rate,

    -- rushing volume + efficiency
    sum(rushing_attempts)               AS rush_att,
    sum(rushing_yards)                  AS rush_yds,
    sum(rushing_tds)                    AS rush_td,
    if(sum(rushing_attempts) > 0, sum(rushing_yards) / sum(rushing_attempts), NULL)   AS yds_per_carry,
    if(sum(rushing_attempts) > 0, sum(rushing_tds) / sum(rushing_attempts), NULL)     AS rush_td_rate,

    -- receiving volume + efficiency
    sum(targets)                        AS total_targets,
    sum(receptions)                     AS total_receptions,
    sum(receiving_yards)                AS rec_yds,
    sum(receiving_tds)                  AS rec_td,
    if(sum(targets) > 0, sum(receptions) / sum(targets), NULL)          AS catch_rate,
    if(sum(targets) > 0, sum(receiving_yards) / sum(targets), NULL)     AS yds_per_target,
    if(sum(receptions) > 0, sum(receiving_yards) / sum(receptions), NULL) AS yds_per_reception,

    -- ball security
    sum(fumbles)                        AS total_fumbles,
    sum(fumbles_lost)                   AS total_fumbles_lost,

    -- team context (avg per game the player appeared in — proxy for
    -- offensive environment quality)
    avg(total_plays)                    AS team_plays_pg,
    avg(yards_per_play)                 AS team_yards_per_play,
    avg(total_drives)                   AS team_drives_pg,
    if(sum(red_zone_attempts) > 0, sum(red_zone_conversions) / sum(red_zone_attempts), NULL) AS team_rz_conv_rate,
    avg(possession_time_seconds)        AS team_possession_secs,
    avg(turnovers)                      AS team_turnovers_pg,

    -- team pass/rush volume — used downstream to compute target share and
    -- rush share (this player's volume ÷ team's total volume), a stronger
    -- predictor of repeat fantasy value than raw target/carry counts since
    -- it captures role independent of how pass/run-heavy the team is
    sum(team_passing_attempts)          AS team_pass_att_sum,
    sum(team_rushing_attempts)          AS team_rush_att_sum,

    -- within-season trend: last 4 games played vs full-season ppg
    -- (positive gap = trending up, negative = trending down / role shrinking)
    avgIf(fantasy_points, games_from_end <= 4) AS ppg_last4,

    -- ADP (already joined at player_name+season grain upstream; NULL for
    -- seasons where no ADP data exists)
    any(adp)                            AS adp

FROM ranked
GROUP BY player_id, season
ORDER BY player_id, season;
