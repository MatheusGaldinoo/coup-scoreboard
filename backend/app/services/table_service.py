import re
import unicodedata
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.table import Table

def generate_slug_base(name: str) -> str:
    # Remove acentos
    normalized = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    # Tudo minusculo
    normalized = normalized.lower()
    # Substitui caracteres que nao sao letras/numeros por hifen
    slug = re.sub(r'[^a-z0-9]+', '-', normalized)
    return slug.strip('-')

async def create_table(db: AsyncSession, name: str) -> Table:
    base_slug = generate_slug_base(name)
    if not base_slug:
        base_slug = "mesa"

    slug = base_slug
    counter = 1
    
    # Busca por colisao de slug
    while True:
        result = await db.execute(select(Table).where(Table.slug == slug))
        if result.scalar_one_or_none() is None:
            break
        counter += 1
        slug = f"{base_slug}-{counter}"

    new_table = Table(name=name, slug=slug)
    db.add(new_table)
    await db.commit()
    await db.refresh(new_table)
    return new_table

async def get_table_by_slug(db: AsyncSession, slug: str) -> Table | None:
    result = await db.execute(select(Table).where(Table.slug == slug))
    return result.scalar_one_or_none()
