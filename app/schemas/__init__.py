from app.schemas.alerta import AlertaRead
from app.schemas.corrego import CorregoCreate, CorregoRead, CorregoStatus, CorregoUpdate
from app.schemas.leitura import LeituraCreate, LeituraRead, LeituraRegistrada
from app.schemas.morador import MoradorCreate, MoradorRead, MoradorResumo, MoradorUpdate
from app.schemas.sensor import SensorCreate, SensorRead

__all__ = [
    "AlertaRead",
    "CorregoCreate",
    "CorregoRead",
    "CorregoStatus",
    "CorregoUpdate",
    "LeituraCreate",
    "LeituraRead",
    "LeituraRegistrada",
    "MoradorCreate",
    "MoradorRead",
    "MoradorResumo",
    "MoradorUpdate",
    "SensorCreate",
    "SensorRead",
]
