from fastapi import APIRouter

from app.api.routes import inference, compile
from app.common import stub

api_router = APIRouter()
api_router.include_router(inference.router, prefix="/inference", tags=["inference"])
api_router.include_router(compile.router, prefix="/compile", tags=["compile"])
