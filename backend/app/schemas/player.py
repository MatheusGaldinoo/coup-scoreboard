from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class PlayerBase(BaseModel):
    name: str

class PlayerCreate(PlayerBase):
    pass

class PlayerOut(PlayerBase):
    id: UUID
    table_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
