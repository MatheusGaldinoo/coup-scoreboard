from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    
    action_type = Column(String(30), nullable=False)
    event_type = Column(String(30), nullable=False)
    result = Column(String(30), nullable=True)
    details = Column(JSONB, nullable=True)
    turn_number = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    match = relationship("Match", back_populates="events")
    actor = relationship("Player", foreign_keys=[actor_id])
    target = relationship("Player", foreign_keys=[target_id])
