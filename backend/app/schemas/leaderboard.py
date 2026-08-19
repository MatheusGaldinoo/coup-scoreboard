from pydantic import BaseModel
from uuid import UUID

class PlayerRanking(BaseModel):
    player_id: UUID
    player_name: str
    matches_played: int
    wins: int
    win_rate: float
    total_kills: int

class LeaderboardResponse(BaseModel):
    table_slug: str
    period: str
    rankings: list[PlayerRanking]

class PlayerDetailsMatch(BaseModel):
    match_id: UUID
    finished_at: str
    finish_position: int
    kills: int
    was_winner: bool

class PlayerDetailsResponse(BaseModel):
    player_id: UUID
    player_name: str
    total_matches: int
    total_wins: int
    total_kills: int
    challenges_made: int
    challenges_received: int
    match_history: list[PlayerDetailsMatch]
