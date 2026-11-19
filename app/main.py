"""Ponto de entrada da API Alerta Córrego (FastAPI)."""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.core.config import settings
from app.core.exceptions import ErroDeNegocio

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

DESCRICAO = """
API REST da CitizenTech **Alerta Córrego** (FIAP Global Solution — SOA e Web Services).

Sensores ESP32 instalados em córregos pequenos da Zona Sul de São Paulo enviam o nível da
água e a chuva. A API **classifica o risco** de transbordamento, **gera alertas** e indica
os **moradores prioritários** (idosos e pessoas com mobilidade reduzida) que precisam de
ajuda para sair a tempo.

**Regra de risco**: nível ≥ crítico → `CRITICO`; nível ≥ alerta → `ALERTA`;
nível ≥ 75% do alerta ou chuva ≥ 30 mm/h → `ATENCAO`; senão `NORMAL`.

Todos os JSON usam **camelCase**. Dados de moradores são **fictícios**.
"""

TAGS = [
    {"name": "Córregos", "description": "Córregos monitorados, limites e status atual."},
    {"name": "Sensores", "description": "Sensores ESP32 instalados nos córregos."},
    {"name": "Leituras", "description": "Medições enviadas pelos sensores; geram alertas."},
    {"name": "Moradores", "description": "Moradores cadastrados (dados simulados)."},
    {"name": "Alertas", "description": "Alertas gerados para os córregos."},
    {"name": "Sistema", "description": "Saúde da API."},
]

app = FastAPI(
    title=settings.app_name,
    description=DESCRICAO,
    version=settings.app_version,
    openapi_tags=TAGS,
    contact={"name": "Equipe Alerta Córrego — FIAP"},
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ErroDeNegocio)
async def tratar_erro_de_negocio(_request: Request, exc: ErroDeNegocio) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensagem})


@app.get("/", tags=["Sistema"], summary="Health check")
def raiz() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "versao": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


app.include_router(api_router)
