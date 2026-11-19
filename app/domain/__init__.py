"""Camada de domínio: enums e regras puras (sem FastAPI/SQLAlchemy)."""
from app.domain.enums import NivelRisco, TipoNecessidade
from app.domain.risco import (
    RISCOS_QUE_GERAM_ALERTA,
    classificar_risco,
    deve_gerar_alerta,
    definir_prioridade,
    gerar_mensagem_alerta,
)

__all__ = [
    "NivelRisco",
    "TipoNecessidade",
    "RISCOS_QUE_GERAM_ALERTA",
    "classificar_risco",
    "deve_gerar_alerta",
    "definir_prioridade",
    "gerar_mensagem_alerta",
]
