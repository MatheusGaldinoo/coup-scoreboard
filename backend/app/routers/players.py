from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.schemas.player import PlayerCreate, PlayerOut
from app.models.player import Player
from app.services.table_service import get_table_by_slug

router = APIRouter(prefix="/api/tables/{slug}/players", tags=["players"])

@router.post("", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
async def create_new_player(slug: str, player_data: PlayerCreate, db: AsyncSession = Depends(get_db)):
    table = await get_table_by_slug(db, slug)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    new_player = Player(table_id=table.id, name=player_data.name)
    db.add(new_player)
    
    try:
        await db.commit()
        await db.refresh(new_player)
        return new_player
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Já existe um jogador com este nome nesta mesa.")

@router.get("", response_model=List[PlayerOut])
async def list_players(slug: str, db: AsyncSession = Depends(get_db)):
    table = await get_table_by_slug(db, slug)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    result = await db.execute(select(Player).where(Player.table_id == table.id).order_by(Player.created_at))
    players = result.scalars().all()
    return list(players)
