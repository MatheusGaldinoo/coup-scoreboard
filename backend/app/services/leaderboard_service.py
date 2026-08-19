from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, text
from uuid import UUID
from datetime import datetime, timedelta, timezone

async def get_table_leaderboard(db: AsyncSession, table_id: UUID, slug: str, period: str):
    # Lógica de datas baseada no period
    date_filter = ""
    params = {"table_id": str(table_id)}
    
    if period == "weekly":
        last_week = datetime.now(timezone.utc) - timedelta(days=7)
        date_filter = "AND m.finished_at >= :date_limit"
        params["date_limit"] = last_week
    elif period == "monthly":
        last_month = datetime.now(timezone.utc) - timedelta(days=30)
        date_filter = "AND m.finished_at >= :date_limit"
        params["date_limit"] = last_month

    # Query customizada com raw SQL via text() para simplificar os JOINs do dashboard
    sql = text(f"""
        SELECT 
            p.id as player_id,
            p.name as player_name,
            COUNT(mp.id) as matches_played,
            SUM(CASE WHEN m.winner_id = p.id THEN 1 ELSE 0 END) as wins,
            SUM(mp.kills) as total_kills
        FROM players p
        JOIN match_participations mp ON p.id = mp.player_id
        JOIN matches m ON mp.match_id = m.id
        WHERE p.table_id = :table_id
        AND m.status = 'finished'
        {date_filter}
        GROUP BY p.id, p.name
        ORDER BY wins DESC, total_kills DESC
    """)
    
    result = await db.execute(sql, params)
    rows = result.fetchall()
    
    rankings = []
    for r in rows:
        wins = int(r.wins) if r.wins else 0
        played = int(r.matches_played)
        win_rate = (wins / played * 100) if played > 0 else 0.0
        
        rankings.append({
            "player_id": r.player_id,
            "player_name": r.player_name,
            "matches_played": played,
            "wins": wins,
            "win_rate": round(win_rate, 2),
            "total_kills": int(r.total_kills) if r.total_kills else 0
        })
        
    return {
        "table_slug": slug,
        "period": period,
        "rankings": rankings
    }

async def get_player_details(db: AsyncSession, player_id: UUID):
    # Detalhes básicos e histórico
    sql_matches = text("""
        SELECT 
            m.id as match_id,
            m.finished_at,
            mp.finish_position,
            mp.kills,
            (m.winner_id = :player_id) as was_winner
        FROM match_participations mp
        JOIN matches m ON mp.match_id = m.id
        WHERE mp.player_id = :player_id AND m.status = 'finished'
        ORDER BY m.finished_at DESC
    """)
    
    matches_result = await db.execute(sql_matches, {"player_id": str(player_id)})
    matches_rows = matches_result.fetchall()
    
    if not matches_rows:
        return None
        
    # Agregações via subqueries rápidas
    # Opcionalmente, pode ser melhor buscar o player com ORM antes, mas para simplicidade faremos manual se existirem matches
    # Num cenário ideal o router verifica se o player existe.
    
    sql_player = text("SELECT name FROM players WHERE id = :player_id")
    player_name = (await db.execute(sql_player, {"player_id": str(player_id)})).scalar_one_or_none()
    
    sql_challenges_made = text("SELECT count(id) FROM match_events WHERE actor_id = :player_id AND event_type IN ('challenge', 'challenge_block')")
    challenges_made = (await db.execute(sql_challenges_made, {"player_id": str(player_id)})).scalar() or 0
    
    sql_challenges_rcv = text("SELECT count(id) FROM match_events WHERE target_id = :player_id AND event_type IN ('challenge', 'challenge_block')")
    challenges_received = (await db.execute(sql_challenges_rcv, {"player_id": str(player_id)})).scalar() or 0

    total_matches = len(matches_rows)
    total_wins = sum(1 for m in matches_rows if m.was_winner)
    total_kills = sum(m.kills for m in matches_rows)
    
    history = [
        {
            "match_id": m.match_id,
            "finished_at": m.finished_at.isoformat() if m.finished_at else "",
            "finish_position": m.finish_position or 0,
            "kills": m.kills,
            "was_winner": m.was_winner
        } for m in matches_rows
    ]
    
    return {
        "player_id": player_id,
        "player_name": player_name,
        "total_matches": total_matches,
        "total_wins": total_wins,
        "total_kills": total_kills,
        "challenges_made": challenges_made,
        "challenges_received": challenges_received,
        "match_history": history
    }
