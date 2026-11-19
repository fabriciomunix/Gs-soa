from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Leitura, Sensor


class LeituraRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, corrego_id: int | None = None, limite: int = 50) -> list[Leitura]:
        stmt = select(Leitura).order_by(Leitura.registrada_em.desc(), Leitura.id.desc())
        if corrego_id is not None:
            stmt = stmt.join(Sensor, Sensor.id == Leitura.sensor_id).where(
                Sensor.corrego_id == corrego_id
            )
        return list(self.db.scalars(stmt.limit(limite)))

    def ultima_do_corrego(self, corrego_id: int) -> Leitura | None:
        leituras = self.listar(corrego_id=corrego_id, limite=1)
        return leituras[0] if leituras else None

    def adicionar(self, leitura: Leitura) -> Leitura:
        self.db.add(leitura)
        self.db.flush()
        return leitura
