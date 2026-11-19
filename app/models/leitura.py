from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._util import agora_utc

if TYPE_CHECKING:
    from app.models.sensor import Sensor


class Leitura(Base):
    __tablename__ = "leituras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(
        ForeignKey("sensores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nivel_agua_cm: Mapped[float] = mapped_column(Float, nullable=False)
    chuva_mm_hora: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    registrada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=agora_utc, index=True
    )

    sensor: Mapped[Sensor] = relationship(back_populates="leituras")

    def __repr__(self) -> str:
        return f"<Leitura id={self.id} sensor_id={self.sensor_id} nivel={self.nivel_agua_cm}>"
