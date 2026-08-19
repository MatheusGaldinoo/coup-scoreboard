from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id"), nullable=False)
    winner_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    status = Column(String(20), nullable=False, default="in_progress")
    
    current_turn_player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    turn_phase = Column(String(40), nullable=False, default="awaiting_action")
    pending_action = Column(String(30), nullable=True)
    pending_actor_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    pending_target_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    turn_number = Column(Integer, nullable=False, default=1)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    table = relationship("Table", back_populates="matches")
    winner = relationship("Player", foreign_keys=[winner_id])
    current_turn_player = relationship("Player", foreign_keys=[current_turn_player_id])
    participations = relationship("MatchParticipation", back_populates="match", cascade="all, delete-orphan")
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan", order_by="MatchEvent.created_at")
