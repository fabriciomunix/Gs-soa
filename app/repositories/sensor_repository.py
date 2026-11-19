from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Sensor


class SensorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, corrego_id: int | None = None) -> list[Sensor]:
        stmt = select(Sensor).order_by(Sensor.id)
        if corrego_id is not None:
            stmt = stmt.where(Sensor.corrego_id == corrego_id)
        return list(self.db.scalars(stmt))

    def obter(self, sensor_id: int) -> Sensor | None:
        return self.db.get(Sensor, sensor_id)

    def obter_por_codigo(self, codigo: str) -> Sensor | None:
        return self.db.scalar(select(Sensor).where(Sensor.codigo == codigo))

    def adicionar(self, sensor: Sensor) -> Sensor:
        self.db.add(sensor)
        self.db.flush()
        return sensor
