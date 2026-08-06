"""
Step 6: VORP + Draft Board

League settings (from user): 12 teams, Full PPR, 1QB/2RB/2WR/1TE/1FLEX(RB/WR/TE)

VORP = projected points - replacement level points for that position.
Replacement level = the projection of the last plausible starter at that
position league-wide, accounting for FLEX eligibility (RB/WR/TE all compete
for the FLEX slot, so their effective replacement level sits deeper than
their dedicated-starter count alone would suggest).

This is what makes a WR1 comparable to an RB1 in draft order -- raw
projected points aren't directly comparable across positions because
position scarcity differs.

NOTE: ADP is not yet available in the source data for the 2026 season (see
README/plan doc), so this board is ranked by model VORP only. Once you have
a 2026 ADP source, merge it in on player_name to get the "market value gap"
column that actually flags sleepers/reaches.
"""

import pandas as pd
import numpy as np

N_TEAMS = 12
DEDICATED_STARTERS = {"Quarterback": 1, "Running Back": 2, "Wide Receiver": 2, "Tight End": 1}
FLEX_SLOTS_PER_TEAM = 1
# rough industry-standard split of how FLEX slots get used across RB/WR/TE
# in PPR leagues -- WR and RB dominate, TE rarely flexed except elite tiers
FLEX_SHARE = {"Running Back": 0.40, "Wide Receiver": 0.45, "Tight End": 0.15}


def compute_replacement_ranks() -> dict:
    total_flex = N_TEAMS * FLEX_SLOTS_PER_TEAM
    ranks = {}
    for pos, dedicated in DEDICATED_STARTERS.items():
        flex_alloc = total_flex * FLEX_SHARE.get(pos, 0)
        # +1 to point to the first BENCH-level player, i.e. the replacement
        rank = round(dedicated * N_TEAMS + flex_alloc) + 1
        ranks[pos] = rank
    return ranks


def build_draft_board(projections_csv: str, output_csv: str):
    df = pd.read_csv(projections_csv)
    df = df.sort_values("proj_total_points_2026", ascending=False).reset_index(drop=True)

    replacement_ranks = compute_replacement_ranks()
    print("Replacement level rank by position (12-team, full PPR, 1QB/2RB/2WR/1TE/1FLEX):")
    for pos, rank in replacement_ranks.items():
        print(f"  {pos}: replacement = player ranked #{rank} at the position")

    replacement_points = {}
    for pos, rank in replacement_ranks.items():
        pos_players = df[df["position"] == pos].sort_values("proj_total_points_2026", ascending=False)
        if len(pos_players) >= rank:
            replacement_points[pos] = pos_players.iloc[rank - 1]["proj_total_points_2026"]
        else:
            # not enough projected players at this position to reach replacement
            # rank (can happen with a small predict set) -- fall back to the
            # lowest projected player at the position
            replacement_points[pos] = pos_players["proj_total_points_2026"].min()
        print(f"  {pos} replacement level points: {replacement_points[pos]:.1f}")

    df["replacement_level_points"] = df["position"].map(replacement_points)
    df["vorp"] = df["proj_total_points_2026"] - df["replacement_level_points"]

    df = df.sort_values("vorp", ascending=False).reset_index(drop=True)
    df["draft_rank"] = df.index + 1

    keep_cols = [
        "draft_rank", "player_name", "position", "team_name", "age",
        "proj_total_points_2026", "proj_ppg_2026", "proj_games_2026",
        "replacement_level_points", "vorp",
    ]
    df[keep_cols].to_csv(output_csv, index=False)

    print(f"\nTop 20 draft board by VORP:")
    print(df[keep_cols].head(20).to_string(index=False))
    print(f"\nSaved: {output_csv}")


if __name__ == "__main__":
    build_draft_board(
        projections_csv="data/projections_2026.csv",
        output_csv="data/draft_board_2026.csv",
    )
