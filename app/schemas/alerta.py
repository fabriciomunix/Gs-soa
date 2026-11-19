from datetime import datetime

from app.domain.enums import NivelRisco
from app.schemas.base import CamelModel


class AlertaRead(CamelModel):
    id: int
    corrego_id: int
    nivel_risco: NivelRisco
    mensagem: str
    nivel_agua_cm: float
    criado_em: datetime
    ativo: bool
