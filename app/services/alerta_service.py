from sqlalchemy.orm import Session

from app.core.exceptions import ConflitoDeDados, RecursoNaoEncontrado
from app.models import Alerta
from app.repositories import AlertaRepository


class AlertaService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AlertaRepository(db)

    def listar(self, ativos: bool | None = None, corrego_id: int | None = None) -> list[Alerta]:
        return self.repo.listar(ativos=ativos, corrego_id=corrego_id)

    def encerrar(self, alerta_id: int) -> Alerta:
        alerta = self.repo.obter(alerta_id)
        if alerta is None:
            raise RecursoNaoEncontrado(f"Alerta {alerta_id} não encontrado.")
        if not alerta.ativo:
            raise ConflitoDeDados(f"Alerta {alerta_id} já está encerrado.")
        alerta.ativo = False
        self.db.commit()
        self.db.refresh(alerta)
        return alerta
