from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.core.enums import MatchStatus, TurnPhase

class MatchCreate(BaseModel):
    player_ids: List[UUID]

class MatchEventOut(BaseModel):
    id: UUID
    actor_id: UUID
    target_id: Optional[UUID] = None
    action_type: str
    event_type: str
    result: Optional[str] = None
    details: Optional[dict] = None
    turn_number: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MatchParticipationOut(BaseModel):
    id: UUID
    player_id: UUID
    coins: int
    lives: int
    is_eliminated: bool
    turn_order: int
    finish_position: Optional[int] = None
    kills: int
    
    model_config = ConfigDict(from_attributes=True)

class MatchOut(BaseModel):
    id: UUID
    table_id: UUID
    winner_id: Optional[UUID] = None
    status: MatchStatus
    current_turn_player_id: Optional[UUID] = None
    turn_phase: TurnPhase
    pending_action: Optional[str] = None
    pending_actor_id: Optional[UUID] = None
    pending_target_id: Optional[UUID] = None
    turn_number: int
    created_at: datetime
    finished_at: Optional[datetime] = None
    
    participations: List[MatchParticipationOut] = []
    
    model_config = ConfigDict(from_attributes=True)
