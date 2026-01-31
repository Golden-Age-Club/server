from fastapi import APIRouter

from . import auth, admins, players, games, finance, stats, audit, vip, risk, promotions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admins.router, prefix="/admins", tags=["Admin Management"])
api_router.include_router(players.router, prefix="/players", tags=["Player Management"])
api_router.include_router(games.router, prefix="/games", tags=["Game Management"])
api_router.include_router(finance.router, prefix="/finance", tags=["Finance Management"])
api_router.include_router(stats.router, prefix="/stats", tags=["Dashboard Statistics"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Logs"])
api_router.include_router(vip.router, prefix="/vip", tags=["VIP Management"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Control"])
api_router.include_router(promotions.router, prefix="/promotions", tags=["Promotions Management"])
