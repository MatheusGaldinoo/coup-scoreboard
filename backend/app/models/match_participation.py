from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class MatchParticipation(Base):
    __tablename__ = "match_participations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    
    coins = Column(Integer, nullable=False, default=1)
    lives = Column(Integer, nullable=False, default=2)
    finish_position = Column(Integer, nullable=True)
    kills = Column(Integer, nullable=False, default=0)
    is_eliminated = Column(Boolean, nullable=False, default=False)
    turn_order = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('match_id', 'player_id', name='uq_match_player'),
    )

    match = relationship("Match", back_populates="participations")
    player = relationship("Player", back_populates="participations")
