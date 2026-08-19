from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from app.models.match import Match
from app.models.match_participation import MatchParticipation
from app.models.match_event import MatchEvent
from app.core.enums import TurnPhase, MatchStatus, ActionType, EventType
from app.core.exceptions import GameRuleError

async def _get_match_with_locks(db: AsyncSession, match_id: UUID) -> Match:
    # Em um cenario real, usariamos with_for_update() para evitar concorrência.
    # Mas como é local e o operador é único, selectinload serve bem.
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.participations))
        .where(Match.id == match_id, Match.status == MatchStatus.IN_PROGRESS)
    )
    match = result.scalar_one_or_none()
    if not match:
        raise GameRuleError("Partida não encontrada ou já finalizada.")
    return match

async def _log_event(db: AsyncSession, match: Match, actor_id: UUID, action_type: str, event_type: str, target_id: Optional[UUID] = None, result_str: Optional[str] = None):
    event = MatchEvent(
        match_id=match.id,
        actor_id=actor_id,
        target_id=target_id,
        action_type=action_type,
        event_type=event_type,
        result=result_str,
        turn_number=match.turn_number
    )
    db.add(event)

def _get_player_participation(match: Match, player_id: UUID) -> MatchParticipation:
    for p in match.participations:
        if p.player_id == player_id:
            return p
    raise GameRuleError("Jogador não pertence à partida.")

def _next_turn(match: Match):
    # Encontrar o proximo jogador não eliminado
    current_idx = -1
    parts = sorted(match.participations, key=lambda p: p.turn_order)
    
    alive_players = [p for p in parts if not p.is_eliminated]
    if len(alive_players) <= 1:
        # Fim de jogo
        match.status = MatchStatus.FINISHED
        match.finished_at = datetime.now(timezone.utc)
        if len(alive_players) == 1:
            match.winner_id = alive_players[0].player_id
            alive_players[0].finish_position = 1
        match.turn_phase = TurnPhase.TURN_COMPLETE
        return

    for i, p in enumerate(alive_players):
        if p.player_id == match.current_turn_player_id:
            current_idx = i
            break
            
    next_idx = (current_idx + 1) % len(alive_players)
    match.current_turn_player_id = alive_players[next_idx].player_id
    match.turn_phase = TurnPhase.AWAITING_ACTION
    match.pending_action = None
    match.pending_actor_id = None
    match.pending_target_id = None
    match.turn_number += 1

def _apply_action_effects(match: Match, actor_p: MatchParticipation, target_p: Optional[MatchParticipation]):
    act = match.pending_action
    if act == ActionType.INCOME:
        actor_p.coins += 1
    elif act == ActionType.FOREIGN_AID:
        actor_p.coins += 2
    elif act == ActionType.TAX:
        actor_p.coins += 3
    elif act == ActionType.STEAL:
        stolen = min(2, target_p.coins)
        target_p.coins -= stolen
        actor_p.coins += stolen
    elif act == ActionType.COUP:
        # Perda de vida tratada como pendente ou aplicada direta.
        pass # A UI vai chamar lose_life para o target
    elif act == ActionType.ASSASSINATE:
        # Assassinate tb tira vida do alvo
        pass # UI chama lose_life para o target

async def declare_action(db: AsyncSession, match_id: UUID, actor_id: UUID, action_type: str, target_id: Optional[UUID] = None):
    match = await _get_match_with_locks(db, match_id)
    if match.turn_phase != TurnPhase.AWAITING_ACTION:
        raise GameRuleError("Não é possível declarar ação agora.")
    if match.current_turn_player_id != actor_id:
        raise GameRuleError("Não é o turno deste jogador.")
    
    actor_p = _get_player_participation(match, actor_id)
    
    # Validacoes de ação
    if action_type == ActionType.COUP:
        if actor_p.coins < 7:
            raise GameRuleError("Moedas insuficientes para Golpe (Coup).")
        if not target_id:
            raise GameRuleError("Golpe requer um alvo.")
        actor_p.coins -= 7
    elif action_type == ActionType.ASSASSINATE:
        if actor_p.coins < 3:
            raise GameRuleError("Moedas insuficientes para Assassinar.")
        if not target_id:
            raise GameRuleError("Assassinar requer um alvo.")
        actor_p.coins -= 3
    elif action_type == ActionType.STEAL and not target_id:
        raise GameRuleError("Roubar requer um alvo.")
        
    # Regra D-10: 10 ou mais moedas obriga golpe
    if actor_p.coins >= 10 and action_type != ActionType.COUP:
        raise GameRuleError("Jogador possui 10 ou mais moedas e é obrigado a dar um Golpe (Coup).")

    match.pending_action = action_type
    match.pending_actor_id = actor_id
    match.pending_target_id = target_id
    
    await _log_event(db, match, actor_id, action_type, EventType.ACTION, target_id)

    # Ações sem reação (Income, Coup) vão direto pra resolver
    if action_type in [ActionType.INCOME, ActionType.COUP]:
        match.turn_phase = TurnPhase.RESOLVING
        _apply_action_effects(match, actor_p, _get_player_participation(match, target_id) if target_id else None)
        if action_type == ActionType.INCOME:
            _next_turn(match)
    else:
        match.turn_phase = TurnPhase.AWAITING_REACTION

    await db.commit()
    return match

async def execute_resolution(db: AsyncSession, match_id: UUID):
    # Endpoint pra avancar o turno se ele tiver travado em RESOLVING (ex: apos um Exchange ou perda de vida já computada)
    match = await _get_match_with_locks(db, match_id)
    if match.turn_phase == TurnPhase.RESOLVING:
        _next_turn(match)
        await db.commit()
    return match

async def challenge_action(db: AsyncSession, match_id: UUID, challenger_id: UUID):
    match = await _get_match_with_locks(db, match_id)
    if match.turn_phase != TurnPhase.AWAITING_REACTION:
        raise GameRuleError("Ação não pode ser desafiada neste momento.")
        
    # Se a ação era Foreign Aid, ela não pode ser desafiada, apenas bloqueada (Regra de Coup base).
    if match.pending_action == ActionType.FOREIGN_AID:
        raise GameRuleError("Ajuda Externa (Foreign Aid) não pode ser desafiada, apenas bloqueada.")
        
    match.turn_phase = TurnPhase.AWAITING_CHALLENGE_RESULT
    await _log_event(db, match, challenger_id, match.pending_action, EventType.CHALLENGE, match.pending_actor_id)
    await db.commit()
    return match

async def block_action(db: AsyncSession, match_id: UUID, blocker_id: UUID):
    match = await _get_match_with_locks(db, match_id)
    if match.turn_phase != TurnPhase.AWAITING_REACTION:
        raise GameRuleError("Ação não pode ser bloqueada neste momento.")
        
    if match.pending_action not in [ActionType.FOREIGN_AID, ActionType.ASSASSINATE, ActionType.STEAL]:
        raise GameRuleError("Esta ação não pode ser bloqueada.")
        
    if match.pending_target_id and blocker_id != match.pending_target_id:
        raise GameRuleError("Apenas o alvo pode bloquear esta ação.")
        
    match.turn_phase = TurnPhase.ACTION_BLOCKED
    # O alvo agora é o blocker, quem fez a acao é o actor
    await _log_event(db, match, blocker_id, match.pending_action, EventType.BLOCK, match.pending_actor_id)
    await db.commit()
    return match

async def challenge_block(db: AsyncSession, match_id: UUID, challenger_id: UUID):
    match = await _get_match_with_locks(db, match_id)
    if match.turn_phase != TurnPhase.ACTION_BLOCKED:
        raise GameRuleError("Não há bloqueio para desafiar.")
        
    match.turn_phase = TurnPhase.AWAITING_BLOCK_CHALLENGE_RESULT
    await _log_event(db, match, challenger_id, match.pending_action, EventType.CHALLENGE_BLOCK)
    await db.commit()
    return match

async def resolve_challenge(db: AsyncSession, match_id: UUID, loser_id: UUID):
    # Quem perde o desafio (seja da acao ou do bloqueio) deve perder 1 vida.
    # Esta função apenas anota quem perdeu o desafio e vai para RESOLVING.
    # Mas se quem sofreu a acao principal perdeu o desafio da acao (ex: blefou no assassinato e foi pego), ele perde vida do desafio. Se for assassinato, perde 2? O motor deixa a UI chamar `lose_life` explicitamente as N vezes que forem precisas.
    
    match = await _get_match_with_locks(db, match_id)
    if match.turn_phase not in [TurnPhase.AWAITING_CHALLENGE_RESULT, TurnPhase.AWAITING_BLOCK_CHALLENGE_RESULT]:
        raise GameRuleError("Não há desafio aguardando resolução.")
        
    is_action_challenge = (match.turn_phase == TurnPhase.AWAITING_CHALLENGE_RESULT)
    
    # Se quem perdeu foi o ator original no desafio da ação -> Ação falha, turno encerra.
    # Se quem perdeu foi o desafiante da ação -> Ação passa, entra na resolução normal.
    # Se quem perdeu foi o bloqueador no desafio do bloqueio -> Bloqueio falha, ação passa.
    # Se quem perdeu foi o desafiante do bloqueio -> Bloqueio passa, ação falha.
    
    action_succeeds = False
    
    if is_action_challenge:
        if loser_id == match.pending_actor_id:
            action_succeeds = False
        else:
            action_succeeds = True
    else:
        # Desafio de Bloqueio. 
        # Sabemos que o blocker é quem tentou bloquear. O loser_id pode ser o blocker ou o desafiante.
        # No motor não armazenamos expliciatemente o blocker no estado, mas logicamente: se o loser é o alvo (q bloqueou), a acao passa.
        # Caso contrario, o bloqueio passou.
        if loser_id == match.pending_target_id: # alvo bloqueou e perdeu desafio
            action_succeeds = True
        elif match.pending_action == ActionType.FOREIGN_AID:
             # Foreign aid pode ser bloqueado por qlqr um. Se loser é quem tentou bloquear e falhou, a ação passa.
             # Se for qlqr outra pessoa (desafiou o bloqueio mas o bloqueio era valido), a ação falha.
             # O operador terá que inferir e apenas clicar na UI apropriada, ou o motor pode confiar no estado.
             # Para simplificar: A UI envia quem perdeu vida e nós só perdemos a vida.
            pass
            
    # O mais flexível: A API apenas avança e o front end chama lose_life para o perdedor do desafio.
    # E o frontend dita se a ação segue ou morre baseado na regra, usando `pass_reaction` ou `complete_turn`.
    match.turn_phase = TurnPhase.RESOLVING
    await db.commit()
    return match

async def allow_action(db: AsyncSession, match_id: UUID):
    # Todos passaram e a ação/bloqueio é executada.
    match = await _get_match_with_locks(db, match_id)
    
    if match.turn_phase == TurnPhase.AWAITING_REACTION:
        # Ninguém bloqueou/desafiou, aplica a ação
        actor_p = _get_player_participation(match, match.pending_actor_id)
        target_p = _get_player_participation(match, match.pending_target_id) if match.pending_target_id else None
        _apply_action_effects(match, actor_p, target_p)
        match.turn_phase = TurnPhase.RESOLVING
        
    elif match.turn_phase == TurnPhase.ACTION_BLOCKED:
        # Ninguém desafiou o bloqueio. Ação falha. Vai pro proximo turno.
        match.turn_phase = TurnPhase.RESOLVING
        _next_turn(match)
        
    await db.commit()
    return match

async def lose_life(db: AsyncSession, match_id: UUID, player_id: UUID, killer_id: Optional[UUID] = None):
    match = await _get_match_with_locks(db, match_id)
    target_p = _get_player_participation(match, player_id)
    
    if target_p.lives <= 0:
        raise GameRuleError("Jogador já está eliminado.")
        
    target_p.lives -= 1
    await _log_event(db, match, target_id=player_id, actor_id=killer_id or match.pending_actor_id, action_type="system", event_type=EventType.LOSS_OF_LIFE)
    
    if target_p.lives == 0:
        target_p.is_eliminated = True
        alive_players = [p for p in match.participations if not p.is_eliminated]
        target_p.finish_position = len(alive_players) + 1
        
        await _log_event(db, match, target_id=player_id, actor_id=killer_id or match.pending_actor_id, action_type="system", event_type=EventType.ELIMINATION)
        
        if killer_id:
            killer_p = _get_player_participation(match, killer_id)
            killer_p.kills += 1
            
        # Avaliar fim de jogo
        if len(alive_players) <= 1:
            _next_turn(match) # Vai lidar com o encerramento do jogo
            
    await db.commit()
    return match
