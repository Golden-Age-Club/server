from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Dict, Any

from app.database import get_database
from app.dependencies import get_current_admin
from app.core.permissions import check_permission
from app.schemas.common import ResponseModel

router = APIRouter()

@router.get("/overview", response_model=ResponseModel)
async def get_dashboard_overview(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Get real-time dashboard statistics.
    Calculates GGR, RTP, DAU, and Total Bets.
    """
    if not await check_permission(current_admin, "report:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # 1. Total GGR (Gross Gaming Revenue = Bets - Wins)
    # 2. Total Bets Count
    # 3. RTP (Wins / Bets)
    
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_bets_amount": {"$sum": "$amount"},
                "total_wins_amount": {"$sum": "$win_amount"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    bet_stats = await db.bets.aggregate(pipeline).to_list(1)
    
    if bet_stats:
        stats = bet_stats[0]
        total_bets_amt = stats["total_bets_amount"]
        total_wins_amt = stats["total_wins_amount"]
        total_bets_count = stats["count"]
        ggr = total_bets_amt - total_wins_amt
        rtp = (total_wins_amt / total_bets_amt * 100) if total_bets_amt > 0 else 0
    else:
        ggr = 0.0
        total_bets_count = 0
        rtp = 0.0
        total_bets_amt = 0.0

    # 4. DAU (Daily Active Users - distinct players with activity today)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Active players = those who placed bets OR had transactions today
    betting_players = await db.bets.distinct("player_id", {"created_at": {"$gte": today_start}})
    transacting_players = await db.transactions.distinct("player_id", {"created_at": {"$gte": today_start}})
    new_players = await db.players.distinct("player_id", {"created_at": {"$gte": today_start}})
    
    active_players_set = set(betting_players) | set(transacting_players) | set(new_players)
    dau_count = len(active_players_set)

    # 5. Total Players
    total_players = await db.players.count_documents({})

    return {
        "success": True,
        "data": {
            "ggr": {
                "value": f"${ggr:,.2f}",
                "percentage": 10.5, # Mock trend
                "is_positive": True
            },
            "rtp": {
                "value": f"{rtp:.1f}%",
                "percentage": 0.2,
                "is_positive": True
            },
            "dau": {
                "value": f"{dau_count:,}",
                "percentage": 5.4,
                "is_positive": True
            },
            "bets": {
                "value": f"{total_bets_count:,}",
                "percentage": 3.1,
                "is_positive": True
            },
            "total_players": {
                "value": f"{total_players:,}",
                "percentage": 2.1,
                "is_positive": True
            }
        }
    }
