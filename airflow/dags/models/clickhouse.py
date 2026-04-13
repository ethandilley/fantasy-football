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
