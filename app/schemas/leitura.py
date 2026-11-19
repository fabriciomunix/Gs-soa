from datetime import datetime

from pydantic import Field

from app.domain.enums import NivelRisco
from app.schemas.alerta import AlertaRead
from app.schemas.base import CamelModel
from app.schemas.morador import MoradorResumo


class LeituraCreate(CamelModel):
    """Payload enviado pelo ESP32 a cada medição."""

    sensor_id: int = Field(gt=0, examples=[1])
    nivel_agua_cm: float = Field(ge=0, le=2000, examples=[185.5])
    chuva_mm_hora: float = Field(default=0.0, ge=0, le=500, examples=[42.0])
    registrada_em: datetime | None = Field(
        default=None, description="Se omitido, usa a data/hora do servidor (UTC)."
    )


class LeituraRead(CamelModel):
    id: int
    sensor_id: int
    nivel_agua_cm: float
    chuva_mm_hora: float
    registrada_em: datetime


class LeituraRegistrada(CamelModel):
    """Resposta do POST /api/leituras."""

    leitura: LeituraRead
    nivel_risco: NivelRisco
    alerta: AlertaRead | None = Field(
        default=None, description="Alerta gerado (somente quando ALERTA ou CRITICO)."
    )
    moradores_prioritarios: list[MoradorResumo] = Field(
        default_factory=list,
        description="Moradores prioritários do córrego a notificar/ajudar a sair.",
    )
