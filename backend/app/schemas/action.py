from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ActionDeclare(BaseModel):
    action_type: str
    target_id: Optional[UUID] = None

class ChallengeResolve(BaseModel):
    loser_id: UUID

class LoseLifeDeclare(BaseModel):
    pass # ID vem na URL
