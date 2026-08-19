from app.database import Base
from app.models.table import Table
from app.models.player import Player
from app.models.match import Match
from app.models.match_participation import MatchParticipation
from app.models.match_event import MatchEvent

# Garantindo que o Base.metadata saiba de todos os modelos
__all__ = ["Base", "Table", "Player", "Match", "MatchParticipation", "MatchEvent"]
