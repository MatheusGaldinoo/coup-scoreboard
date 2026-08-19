from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.table import TableCreate, TableOut
from app.services.table_service import create_table, get_table_by_slug

router = APIRouter(prefix="/api/tables", tags=["tables"])

@router.post("", response_model=TableOut, status_code=status.HTTP_201_CREATED)
async def create_new_table(table_data: TableCreate, db: AsyncSession = Depends(get_db)):
    return await create_table(db, table_data.name)

@router.get("/{slug}", response_model=TableOut)
async def get_table(slug: str, db: AsyncSession = Depends(get_db)):
    table = await get_table_by_slug(db, slug)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    return table
