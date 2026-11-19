"""Acesso a dados de córregos (somente SQLAlchemy, sem regra de negócio)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Corrego


class CorregoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self) -> list[Corrego]:
        return list(self.db.scalars(select(Corrego).order_by(Corrego.id)))

    def obter(self, corrego_id: int) -> Corrego | None:
        return self.db.get(Corrego, corrego_id)

    def adicionar(self, corrego: Corrego) -> Corrego:
        self.db.add(corrego)
        self.db.flush()
        return corrego

    def remover(self, corrego: Corrego) -> None:
        self.db.delete(corrego)
        self.db.flush()
