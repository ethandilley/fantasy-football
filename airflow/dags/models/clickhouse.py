from dataclasses import dataclass


@dataclass
class PlayerGameStats:
    # identity
    player_id: int
    name: str | None = None
    game_id: int | None = None
    season: int | None = None
    week: int | None = None

    # passing
    passing_attempts: int = 0
    passing_completions: int = 0
    passing_yards: int = 0
    passing_tds: int = 0
    interceptions: int = 0

    # rushing
    rushing_attempts: int = 0
    rushing_yards: int = 0
    rushing_tds: int = 0

    # receiving
    targets: int = 0
    receptions: int = 0
    receiving_yards: int = 0
    receiving_tds: int = 0

    # fumbles
    fumbles: int = 0
    fumbles_lost: int = 0


@dataclass
class TeamGameStats:
    # identity
    team_id: int
    name: str
    game_id: int
    season: int
    week: int
    home_away: str

    # first downs
    first_downs: int = 0

    # down efficiency
    third_down_conversions: int = 0
    third_down_attempts: int = 0
    fourth_down_conversions: int = 0
    fourth_down_attempts: int = 0

    # overall offense
    total_plays: int = 0
    total_yards: int = 0
    yards_per_play: float = 0.0
    total_drives: int = 0

    # passing
    net_passing_yards: int = 0
    passing_completions: int = 0
    passing_attempts: int = 0
    yards_per_pass: float = 0.0
    interceptions_thrown: int = 0
    sacks: int = 0
    sack_yards_lost: int = 0

    # rushing
    rushing_yards: int = 0
    rushing_attempts: int = 0
    yards_per_rush: float = 0.0

    # red zone
    red_zone_conversions: int = 0
    red_zone_attempts: int = 0

    # turnovers
    turnovers: int = 0
    fumbles_lost: int = 0

    # possession
    possession_time_seconds: int = 0
