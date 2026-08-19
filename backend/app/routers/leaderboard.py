from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.leaderboard import LeaderboardResponse, PlayerDetailsResponse
from app.services.table_service import get_table_by_slug
from app.services.leaderboard_service import get_table_leaderboard, get_player_details
from uuid import UUID

router = APIRouter(prefix="/api/tables/{slug}/leaderboard", tags=["leaderboard"])

@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    slug: str, 
    period: str = Query("all", description="Filtros: weekly, monthly, all"), 
    db: AsyncSession = Depends(get_db)
):
    table = await get_table_by_slug(db, slug)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    return await get_table_leaderboard(db, table.id, slug, period)

@router.get("/{player_id}", response_model=PlayerDetailsResponse)
async def get_player_stats(
    slug: str, 
    player_id: UUID, 
    db: AsyncSession = Depends(get_db)
):
    table = await get_table_by_slug(db, slug)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
        
    stats = await get_player_details(db, player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Jogador não encontrado ou sem histórico")
    return stats
