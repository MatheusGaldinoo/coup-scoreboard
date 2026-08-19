from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.match import MatchOut
from app.schemas.action import ActionDeclare
from app.services.action_service import (
    declare_action, execute_resolution, challenge_action, block_action, 
    challenge_block, resolve_challenge, allow_action, lose_life
)
from uuid import UUID

router = APIRouter(prefix="/api/matches/{match_id}/actions", tags=["match_actions"])

@router.post("/declare", response_model=MatchOut)
async def api_declare_action(match_id: UUID, payload: ActionDeclare, actor_id: UUID, db: AsyncSession = Depends(get_db)):
    # Actor ID poderia vir do auth ou token, mas aqui confiaremos na URL/body (por ser local e sem auth)
    return await declare_action(db, match_id, actor_id, payload.action_type, payload.target_id)

@router.post("/allow", response_model=MatchOut)
async def api_allow_action(match_id: UUID, db: AsyncSession = Depends(get_db)):
    # Usado quando todos dizem "Passo" (Ninguém bloqueia/desafia)
    return await allow_action(db, match_id)

@router.post("/challenge", response_model=MatchOut)
async def api_challenge_action(match_id: UUID, challenger_id: UUID, db: AsyncSession = Depends(get_db)):
    return await challenge_action(db, match_id, challenger_id)

@router.post("/block", response_model=MatchOut)
async def api_block_action(match_id: UUID, blocker_id: UUID, db: AsyncSession = Depends(get_db)):
    return await block_action(db, match_id, blocker_id)

@router.post("/challenge-block", response_model=MatchOut)
async def api_challenge_block(match_id: UUID, challenger_id: UUID, db: AsyncSession = Depends(get_db)):
    return await challenge_block(db, match_id, challenger_id)

@router.post("/resolve-challenge", response_model=MatchOut)
async def api_resolve_challenge(match_id: UUID, loser_id: UUID, db: AsyncSession = Depends(get_db)):
    return await resolve_challenge(db, match_id, loser_id)

@router.post("/lose-life", response_model=MatchOut)
async def api_lose_life(match_id: UUID, target_id: UUID, killer_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    return await lose_life(db, match_id, target_id, killer_id)

@router.post("/next-turn", response_model=MatchOut)
async def api_next_turn(match_id: UUID, db: AsyncSession = Depends(get_db)):
    return await execute_resolution(db, match_id)
