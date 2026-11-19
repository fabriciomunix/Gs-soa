from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoDeDados, RecursoNaoEncontrado
from app.models import Sensor
from app.repositories import CorregoRepository, SensorRepository
from app.schemas import SensorCreate


class SensorService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SensorRepository(db)

    def listar(self, corrego_id: int | None = None) -> list[Sensor]:
        return self.repo.listar(corrego_id)

    def obter(self, sensor_id: int) -> Sensor:
        sensor = self.repo.obter(sensor_id)
        if sensor is None:
            raise RecursoNaoEncontrado(f"Sensor {sensor_id} não encontrado.")
        return sensor

    def criar(self, dados: SensorCreate) -> Sensor:
        if CorregoRepository(self.db).obter(dados.corrego_id) is None:
            raise RecursoNaoEncontrado(f"Córrego {dados.corrego_id} não encontrado.")
        if self.repo.obter_por_codigo(dados.codigo) is not None:
            raise ConflitoDeDados(f"Já existe um sensor com o código {dados.codigo}.")
        sensor = Sensor(
            codigo=dados.codigo,
            corrego_id=dados.corrego_id,
            ativo=dados.ativo,
            instalado_em=dados.instalado_em or datetime.now(timezone.utc),
        )
        self.repo.adicionar(sensor)
        self.db.commit()
        self.db.refresh(sensor)
        return sensor
