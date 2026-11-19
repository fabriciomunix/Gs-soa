from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._util import agora_utc

if TYPE_CHECKING:
    from app.models.corrego import Corrego
    from app.models.leitura import Leitura


class Sensor(Base):
    __tablename__ = "sensores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    corrego_id: Mapped[int] = mapped_column(
        ForeignKey("corregos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    instalado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=agora_utc
    )

    corrego: Mapped[Corrego] = relationship(back_populates="sensores")
    leituras: Mapped[list[Leitura]] = relationship(
        back_populates="sensor", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Sensor id={self.id} codigo={self.codigo!r}>"
