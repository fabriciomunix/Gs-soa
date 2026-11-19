from datetime import datetime

from pydantic import Field, model_validator

from app.domain.enums import NivelRisco
from app.schemas.base import CamelModel
from app.schemas.leitura import LeituraRead


class CorregoBase(CamelModel):
    nome: str = Field(min_length=3, max_length=120, examples=["Córrego Ponte Baixa"])
    bairro: str = Field(min_length=2, max_length=120, examples=["M'Boi Mirim"])
    latitude: float = Field(ge=-90, le=90, examples=[-23.6667])
    longitude: float = Field(ge=-180, le=180, examples=[-46.7667])
    nivel_alerta_cm: float = Field(gt=0, le=2000, examples=[120])
    nivel_critico_cm: float = Field(gt=0, le=2000, examples=[180])


class CorregoCreate(CorregoBase):
    @model_validator(mode="after")
    def validar_limites(self) -> "CorregoCreate":
        if self.nivel_critico_cm <= self.nivel_alerta_cm:
            raise ValueError("nivelCriticoCm deve ser maior que nivelAlertaCm")
        return self


class CorregoUpdate(CamelModel):
    """Atualização parcial: envie apenas os campos que deseja alterar."""

    nome: str | None = Field(default=None, min_length=3, max_length=120)
    bairro: str | None = Field(default=None, min_length=2, max_length=120)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    nivel_alerta_cm: float | None = Field(default=None, gt=0, le=2000)
    nivel_critico_cm: float | None = Field(default=None, gt=0, le=2000)

    @model_validator(mode="after")
    def validar_limites(self) -> "CorregoUpdate":
        if (
            self.nivel_alerta_cm is not None
            and self.nivel_critico_cm is not None
            and self.nivel_critico_cm <= self.nivel_alerta_cm
        ):
            raise ValueError("nivelCriticoCm deve ser maior que nivelAlertaCm")
        return self


class CorregoRead(CorregoBase):
    id: int


class CorregoStatus(CamelModel):
    corrego_id: int
    nome: str
    nivel_agua_cm: float | None = Field(description="Nível da última leitura (cm)")
    chuva_mm_hora: float | None = Field(description="Chuva da última leitura (mm/h)")
    nivel_risco: NivelRisco
    atualizado_em: datetime | None = None
    alertas_ativos: int = 0
    ultima_leitura: LeituraRead | None = None
