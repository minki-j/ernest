from fastapi import APIRouter

from app.api.routes import chat, history

api_router = APIRouter()
api_router.include_router(
    chat.router, prefix="/chat", tags=["chat"]
)

api_router.include_router(
    history.router, prefix="/history", tags=["history"]
)
