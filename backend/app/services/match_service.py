from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc
from uuid import UUID
import random
from typing import List

from app.models.match import Match
from app.models.match_participation import MatchParticipation
from app.models.player import Player
from app.models.table import Table
from app.core.enums import MatchStatus, TurnPhase
from app.core.exceptions import GameRuleError

async def create_match(db: AsyncSession, table_id: UUID, player_ids: List[UUID]) -> Match:
    # Validações
    if len(player_ids) < 4 or len(player_ids) > 6:
        raise GameRuleError("Uma partida de Coup requer entre 4 e 6 jogadores.")
    
    if len(set(player_ids)) != len(player_ids):
        raise GameRuleError("A lista de jogadores contém duplicatas.")

    # Obter os jogadores para garantir que existem e são da mesa
    players_result = await db.execute(select(Player).where(Player.id.in_(player_ids), Player.table_id == table_id))
    players = players_result.scalars().all()
    if len(players) != len(player_ids):
        raise GameRuleError("Alguns jogadores não foram encontrados na mesa.")

    # Verificar ordem do turno (Aleatório se for a primeira, caso contrário: último vencedor)
    last_match_result = await db.execute(
        select(Match).where(Match.table_id == table_id, Match.status == MatchStatus.FINISHED)
        .order_by(desc(Match.finished_at)).limit(1)
    )
    last_match = last_match_result.scalar_one_or_none()

    starting_player_id = None
    if last_match and last_match.winner_id in player_ids:
        starting_player_id = last_match.winner_id
    else:
        starting_player_id = random.choice(player_ids)

    # Determinar ordem do turno circular
    random.shuffle(player_ids) # Sempre embaralhar para definir assentos
    # Mover o starting_player para o índice 0
    starting_index = player_ids.index(starting_player_id)
    ordered_player_ids = player_ids[starting_index:] + player_ids[:starting_index]

    new_match = Match(
        table_id=table_id,
        status=MatchStatus.IN_PROGRESS,
        current_turn_player_id=starting_player_id,
        turn_phase=TurnPhase.AWAITING_ACTION,
        turn_number=1
    )
    db.add(new_match)
    await db.flush() # Para gerar ID do match

    # Criar participações
    for idx, pid in enumerate(ordered_player_ids):
        # Regra D-8: O último vencedor começa com 0 moedas, os outros com 1.
        # No entanto, se não teve último match e é aleatório, todos começam com 1. (Mas para seguir estritamente: "O vencedor da partida anterior começa a nova partida com 0 moedas, enquanto os demais com 1. (Se for a primeira partida, todos com 1 e ordem aleatória)")
        starting_coins = 1
        if last_match and pid == last_match.winner_id:
            starting_coins = 0

        participation = MatchParticipation(
            match_id=new_match.id,
            player_id=pid,
            coins=starting_coins,
            lives=2,
            turn_order=idx,
            is_eliminated=False,
            kills=0
        )
        db.add(participation)

    await db.commit()
    
    # Reload with participations
    result = await db.execute(select(Match).options(selectinload(Match.participations)).where(Match.id == new_match.id))
    return result.scalar_one()

async def get_active_match(db: AsyncSession, table_id: UUID) -> Match | None:
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.participations))
        .where(Match.table_id == table_id, Match.status == MatchStatus.IN_PROGRESS)
    )
    return result.scalar_one_or_none()

async def get_match_by_id(db: AsyncSession, match_id: UUID) -> Match | None:
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.participations))
        .where(Match.id == match_id)
    )
    return result.scalar_one_or_none()

async def cancel_match(db: AsyncSession, match_id: UUID):
    match = await get_match_by_id(db, match_id)
    if not match:
        raise GameRuleError("Partida não encontrada")
    if match.status != MatchStatus.IN_PROGRESS:
        raise GameRuleError("Apenas partidas em progresso podem ser canceladas")
    
    match.status = MatchStatus.CANCELLED
    await db.commit()
    return match
