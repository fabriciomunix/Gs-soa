from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import NivelRisco
from app.models._util import agora_utc

if TYPE_CHECKING:
    from app.models.corrego import Corrego


class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    corrego_id: Mapped[int] = mapped_column(
        ForeignKey("corregos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nivel_risco: Mapped[NivelRisco] = mapped_column(
        SAEnum(NivelRisco, name="nivel_risco", native_enum=False, length=20), nullable=False
    )
    mensagem: Mapped[str] = mapped_column(String(500), nullable=False)
    nivel_agua_cm: Mapped[float] = mapped_column(Float, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=agora_utc, index=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    corrego: Mapped[Corrego] = relationship(back_populates="alertas")

    def __repr__(self) -> str:
        return f"<Alerta id={self.id} corrego_id={self.corrego_id} risco={self.nivel_risco}>"
