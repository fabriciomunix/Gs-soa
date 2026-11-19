"""Modelos ORM. Importar este pacote registra todas as tabelas em Base.metadata."""
from app.models.alerta import Alerta
from app.models.corrego import Corrego
from app.models.leitura import Leitura
from app.models.morador import Morador
from app.models.sensor import Sensor

__all__ = ["Alerta", "Corrego", "Leitura", "Morador", "Sensor"]
