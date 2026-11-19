"""Caso de uso central: registrar leitura do sensor, classificar risco e gerar alerta."""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNaoEncontrado, RegraNegocioViolada
from app.domain import classificar_risco, deve_gerar_alerta, gerar_mensagem_alerta
from app.models import Alerta, Leitura
from app.repositories import (
    AlertaRepository,
    CorregoRepository,
    LeituraRepository,
    MoradorRepository,
    SensorRepository,
)
from app.schemas import (
    AlertaRead,
    LeituraCreate,
    LeituraRead,
    LeituraRegistrada,
    MoradorResumo,
)

logger = logging.getLogger("alerta_corrego.leituras")


class LeituraService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.leituras = LeituraRepository(db)
        self.sensores = SensorRepository(db)
        self.alertas = AlertaRepository(db)
        self.moradores = MoradorRepository(db)

    def listar(self, corrego_id: int | None = None, limite: int = 50) -> list[Leitura]:
        if corrego_id is not None and CorregoRepository(self.db).obter(corrego_id) is None:
            raise RecursoNaoEncontrado(f"Córrego {corrego_id} não encontrado.")
        return self.leituras.listar(corrego_id=corrego_id, limite=limite)

    def registrar(self, dados: LeituraCreate) -> LeituraRegistrada:
        sensor = self.sensores.obter(dados.sensor_id)
        if sensor is None:
            raise RecursoNaoEncontrado(f"Sensor {dados.sensor_id} não encontrado.")
        if not sensor.ativo:
            raise RegraNegocioViolada(f"Sensor {sensor.codigo} está inativo.")

        corrego = sensor.corrego
        leitura = Leitura(
            sensor_id=sensor.id,
            nivel_agua_cm=dados.nivel_agua_cm,
            chuva_mm_hora=dados.chuva_mm_hora,
            registrada_em=dados.registrada_em or datetime.now(timezone.utc),
        )
        self.leituras.adicionar(leitura)

        risco = classificar_risco(
            dados.nivel_agua_cm,
            dados.chuva_mm_hora,
            corrego.nivel_alerta_cm,
            corrego.nivel_critico_cm,
        )

        alerta: Alerta | None = None
        prioritarios = []
        if deve_gerar_alerta(risco):
            alerta = Alerta(
                corrego_id=corrego.id,
                nivel_risco=risco,
                mensagem=gerar_mensagem_alerta(corrego.nome, dados.nivel_agua_cm, risco),
                nivel_agua_cm=dados.nivel_agua_cm,
                ativo=True,
            )
            self.alertas.adicionar(alerta)
            prioritarios = self.moradores.listar_prioritarios(corrego.id)

        self.db.commit()
        self.db.refresh(leitura)
        if alerta is not None:
            self.db.refresh(alerta)
            # Log sem dados pessoais: apenas IDs e contagens.
            logger.warning(
                "Alerta %s gerado: corrego_id=%s risco=%s prioritarios=%d",
                alerta.id,
                corrego.id,
                risco.value,
                len(prioritarios),
            )
        else:
            logger.info("Leitura %s registrada: sensor_id=%s risco=%s", leitura.id, sensor.id, risco.value)

        return LeituraRegistrada(
            leitura=LeituraRead.model_validate(leitura),
            nivel_risco=risco,
            alerta=AlertaRead.model_validate(alerta) if alerta is not None else None,
            moradores_prioritarios=[MoradorResumo.model_validate(m) for m in prioritarios],
        )
