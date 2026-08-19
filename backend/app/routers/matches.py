from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.match import MatchCreate, MatchOut
from app.services.table_service import get_table_by_slug
from app.services.match_service import create_match, get_active_match, cancel_match
from uuid import UUID

router = APIRouter(prefix="/api/tables/{slug}/matches", tags=["matches"])

@router.post("", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
async def start_match(slug: str, match_data: MatchCreate, db: AsyncSession = Depends(get_db)):
    table = await get_table_by_slug(db, slug)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    active_match = await get_active_match(db, table.id)
    if active_match:
        raise HTTPException(status_code=400, detail="Já existe uma partida em andamento nesta mesa")
        
    return await create_match(db, table.id, match_data.player_ids)

@router.get("/active", response_model=MatchOut)
async def get_current_match(slug: str, db: AsyncSession = Depends(get_db)):
    table = await get_table_by_slug(db, slug)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
        
    match = await get_active_match(db, table.id)
    if not match:
        raise HTTPException(status_code=404, detail="Nenhuma partida em andamento")
    return match

@router.post("/{match_id}/cancel", response_model=MatchOut)
async def cancel_active_match(slug: str, match_id: UUID, db: AsyncSession = Depends(get_db)):
    table = await get_table_by_slug(db, slug)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
        
    return await cancel_match(db, match_id)
