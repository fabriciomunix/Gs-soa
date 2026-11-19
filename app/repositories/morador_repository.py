from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Morador


class MoradorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, corrego_id: int | None = None) -> list[Morador]:
        stmt = select(Morador).order_by(Morador.id)
        if corrego_id is not None:
            stmt = stmt.where(Morador.corrego_id == corrego_id)
        return list(self.db.scalars(stmt))

    def listar_prioritarios(self, corrego_id: int | None = None) -> list[Morador]:
        stmt = select(Morador).where(Morador.prioritario.is_(True)).order_by(Morador.id)
        if corrego_id is not None:
            stmt = stmt.where(Morador.corrego_id == corrego_id)
        return list(self.db.scalars(stmt))

    def obter(self, morador_id: int) -> Morador | None:
        return self.db.get(Morador, morador_id)

    def adicionar(self, morador: Morador) -> Morador:
        self.db.add(morador)
        self.db.flush()
        return morador

    def remover(self, morador: Morador) -> None:
        self.db.delete(morador)
        self.db.flush()
