from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Alerta


class AlertaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, ativos: bool | None = None, corrego_id: int | None = None) -> list[Alerta]:
        stmt = select(Alerta).order_by(Alerta.criado_em.desc(), Alerta.id.desc())
        if ativos is not None:
            stmt = stmt.where(Alerta.ativo.is_(ativos))
        if corrego_id is not None:
            stmt = stmt.where(Alerta.corrego_id == corrego_id)
        return list(self.db.scalars(stmt))

    def contar_ativos(self, corrego_id: int) -> int:
        stmt = select(func.count(Alerta.id)).where(
            Alerta.corrego_id == corrego_id, Alerta.ativo.is_(True)
        )
        return int(self.db.scalar(stmt) or 0)

    def obter(self, alerta_id: int) -> Alerta | None:
        return self.db.get(Alerta, alerta_id)

    def adicionar(self, alerta: Alerta) -> Alerta:
        self.db.add(alerta)
        self.db.flush()
        return alerta
