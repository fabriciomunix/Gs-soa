"""Regras de negócio de córregos."""
from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontrado, RegraNegocioViolada
from app.domain import NivelRisco, classificar_risco
from app.models import Corrego
from app.repositories import AlertaRepository, CorregoRepository, LeituraRepository
from app.schemas import CorregoCreate, CorregoStatus, CorregoUpdate, LeituraRead


class CorregoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CorregoRepository(db)

    def listar(self) -> list[Corrego]:
        return self.repo.listar()

    def obter(self, corrego_id: int) -> Corrego:
        corrego = self.repo.obter(corrego_id)
        if corrego is None:
            raise RecursoNaoEncontrado(f"Córrego {corrego_id} não encontrado.")
        return corrego

    def criar(self, dados: CorregoCreate) -> Corrego:
        corrego = Corrego(**dados.model_dump())
        self.repo.adicionar(corrego)
        self.db.commit()
        self.db.refresh(corrego)
        return corrego

    def atualizar(self, corrego_id: int, dados: CorregoUpdate) -> Corrego:
        corrego = self.obter(corrego_id)
        alteracoes = dados.model_dump(exclude_unset=True, exclude_none=True)
        alerta = alteracoes.get("nivel_alerta_cm", corrego.nivel_alerta_cm)
        critico = alteracoes.get("nivel_critico_cm", corrego.nivel_critico_cm)
        if critico <= alerta:
            raise RegraNegocioViolada("nivelCriticoCm deve ser maior que nivelAlertaCm.")
        for campo, valor in alteracoes.items():
            setattr(corrego, campo, valor)
        self.db.commit()
        self.db.refresh(corrego)
        return corrego

    def remover(self, corrego_id: int) -> None:
        corrego = self.obter(corrego_id)
        self.repo.remover(corrego)
        self.db.commit()

    def status(self, corrego_id: int) -> CorregoStatus:
        corrego = self.obter(corrego_id)
        ultima = LeituraRepository(self.db).ultima_do_corrego(corrego_id)
        alertas_ativos = AlertaRepository(self.db).contar_ativos(corrego_id)
        if ultima is None:
            return CorregoStatus(
                corrego_id=corrego.id,
                nome=corrego.nome,
                nivel_agua_cm=None,
                chuva_mm_hora=None,
                nivel_risco=NivelRisco.NORMAL,
                atualizado_em=None,
                alertas_ativos=alertas_ativos,
                ultima_leitura=None,
            )
        risco = classificar_risco(
            ultima.nivel_agua_cm,
            ultima.chuva_mm_hora,
            corrego.nivel_alerta_cm,
            corrego.nivel_critico_cm,
        )
        return CorregoStatus(
            corrego_id=corrego.id,
            nome=corrego.nome,
            nivel_agua_cm=ultima.nivel_agua_cm,
            chuva_mm_hora=ultima.chuva_mm_hora,
            nivel_risco=risco,
            atualizado_em=ultima.registrada_em,
            alertas_ativos=alertas_ativos,
            ultima_leitura=LeituraRead.model_validate(ultima),
        )
