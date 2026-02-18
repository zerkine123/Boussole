# ============================================
# Boussole - API Router
# ============================================

from fastapi import APIRouter

from app.api.v1.endpoints import auth, data, analytics, sectors, onboarding, dashboard, subscription, stripe, search, chat # , rag

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
# api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(sectors.router, prefix="/sectors", tags=["sectors"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(subscription.router, prefix="/subscription", tags=["subscription"])
api_router.include_router(stripe.router, prefix="/stripe", tags=["stripe"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
