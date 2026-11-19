from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alerta import Alerta
    from app.models.morador import Morador
    from app.models.sensor import Sensor


class Corrego(Base):
    __tablename__ = "corregos"
    __table_args__ = (
        CheckConstraint("nivel_critico_cm > nivel_alerta_cm", name="ck_corregos_limites"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    bairro: Mapped[str] = mapped_column(String(120), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    nivel_alerta_cm: Mapped[float] = mapped_column(Float, nullable=False)
    nivel_critico_cm: Mapped[float] = mapped_column(Float, nullable=False)

    sensores: Mapped[list[Sensor]] = relationship(
        back_populates="corrego", cascade="all, delete-orphan", passive_deletes=True
    )
    moradores: Mapped[list[Morador]] = relationship(
        back_populates="corrego", cascade="all, delete-orphan", passive_deletes=True
    )
    alertas: Mapped[list[Alerta]] = relationship(
        back_populates="corrego", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Corrego id={self.id} nome={self.nome!r}>"
