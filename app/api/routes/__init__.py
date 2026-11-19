from fastapi import APIRouter

from app.api.routes import alertas, corregos, leituras, moradores, sensores

api_router = APIRouter(prefix="/api")
api_router.include_router(corregos.router)
api_router.include_router(sensores.router)
api_router.include_router(leituras.router)
api_router.include_router(moradores.router)
api_router.include_router(alertas.router)
