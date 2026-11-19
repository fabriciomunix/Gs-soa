from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontrado
from app.domain import definir_prioridade
from app.models import Morador
from app.repositories import CorregoRepository, MoradorRepository
from app.schemas import MoradorCreate, MoradorUpdate


class MoradorService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MoradorRepository(db)

    def _garantir_corrego(self, corrego_id: int) -> None:
        if CorregoRepository(self.db).obter(corrego_id) is None:
            raise RecursoNaoEncontrado(f"Córrego {corrego_id} não encontrado.")

    def listar(self, corrego_id: int | None = None) -> list[Morador]:
        return self.repo.listar(corrego_id)

    def listar_prioritarios(self, corrego_id: int | None = None) -> list[Morador]:
        if corrego_id is not None:
            self._garantir_corrego(corrego_id)
        return self.repo.listar_prioritarios(corrego_id)

    def obter(self, morador_id: int) -> Morador:
        morador = self.repo.obter(morador_id)
        if morador is None:
            raise RecursoNaoEncontrado(f"Morador {morador_id} não encontrado.")
        return morador

    def criar(self, dados: MoradorCreate) -> Morador:
        self._garantir_corrego(dados.corrego_id)
        valores = dados.model_dump()
        valores["prioritario"] = definir_prioridade(dados.tipo_necessidade, dados.prioritario)
        morador = Morador(**valores)
        self.repo.adicionar(morador)
        self.db.commit()
        self.db.refresh(morador)
        return morador

    def atualizar(self, morador_id: int, dados: MoradorUpdate) -> Morador:
        morador = self.obter(morador_id)
        alteracoes = dados.model_dump(exclude_unset=True, exclude_none=True)
        if "corrego_id" in alteracoes:
            self._garantir_corrego(alteracoes["corrego_id"])
        for campo, valor in alteracoes.items():
            setattr(morador, campo, valor)
        morador.prioritario = definir_prioridade(morador.tipo_necessidade, morador.prioritario)
        self.db.commit()
        self.db.refresh(morador)
        return morador

    def remover(self, morador_id: int) -> None:
        morador = self.obter(morador_id)
        self.repo.remover(morador)
        self.db.commit()
