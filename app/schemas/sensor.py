from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelModel


class SensorCreate(CamelModel):
    codigo: str = Field(
        min_length=3, max_length=50, pattern=r"^[A-Za-z0-9\-_]+$", examples=["ESP32-PB-02"]
    )
    corrego_id: int = Field(gt=0, examples=[1])
    ativo: bool = True
    instalado_em: datetime | None = Field(
        default=None, description="Se omitido, usa a data/hora atual (UTC)."
    )


class SensorRead(CamelModel):
    id: int
    codigo: str
    corrego_id: int
    ativo: bool
    instalado_em: datetime
