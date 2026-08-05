-- =====================================================================
-- 2026 ADP export
-- Filtered to match the user's actual league: 12 teams, full PPR
-- =====================================================================

SELECT
    player_name,
    position,
    adp,
    times_drafted,
    high,
    low,
    stdev,
    total_drafts,
    start_date,
    end_date
FROM silver.adp
WHERE season = 2026
  AND scoring_format = 'PPR'
  AND teams = 12
ORDER BY adp;
