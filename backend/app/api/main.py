from fastapi import APIRouter

from app.api.routes import chat, db


api_router = APIRouter()
api_router.include_router(
    chat.router, prefix="/chat", tags=["chat"]
)

api_router.include_router(
    db.router, prefix="/db", tags=["db"]
)
