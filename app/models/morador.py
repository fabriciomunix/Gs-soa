from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import TipoNecessidade
from app.models._util import agora_utc

if TYPE_CHECKING:
    from app.models.corrego import Corrego


class Morador(Base):
    """Dados SIMULADOS. Nunca registrar nome/telefone/endereço em log."""

    __tablename__ = "moradores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    endereco: Mapped[str] = mapped_column(String(200), nullable=False)
    corrego_id: Mapped[int] = mapped_column(
        ForeignKey("corregos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prioritario: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tipo_necessidade: Mapped[TipoNecessidade] = mapped_column(
        SAEnum(TipoNecessidade, name="tipo_necessidade", native_enum=False, length=20),
        nullable=False,
        default=TipoNecessidade.NENHUMA,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=agora_utc
    )

    corrego: Mapped[Corrego] = relationship(back_populates="moradores")

    def __repr__(self) -> str:  # sem dados pessoais
        return f"<Morador id={self.id} corrego_id={self.corrego_id}>"
