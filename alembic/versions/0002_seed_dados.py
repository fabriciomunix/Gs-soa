"""Seed com dados SIMULADOS (córregos, sensores, moradores fictícios, leituras e 1 alerta).

Revision ID: 0002_seed_dados
Revises: 0001_criar_tabelas
Create Date: 2026-11-19
"""
from datetime import datetime, timedelta, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_seed_dados"
down_revision: Union[str, None] = "0001_criar_tabelas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BASE = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)

corregos = sa.table(
    "corregos",
    sa.column("id", sa.Integer),
    sa.column("nome", sa.String),
    sa.column("bairro", sa.String),
    sa.column("latitude", sa.Float),
    sa.column("longitude", sa.Float),
    sa.column("nivel_alerta_cm", sa.Float),
    sa.column("nivel_critico_cm", sa.Float),
)
sensores = sa.table(
    "sensores",
    sa.column("id", sa.Integer),
    sa.column("codigo", sa.String),
    sa.column("corrego_id", sa.Integer),
    sa.column("ativo", sa.Boolean),
    sa.column("instalado_em", sa.DateTime(timezone=True)),
)
leituras = sa.table(
    "leituras",
    sa.column("id", sa.Integer),
    sa.column("sensor_id", sa.Integer),
    sa.column("nivel_agua_cm", sa.Float),
    sa.column("chuva_mm_hora", sa.Float),
    sa.column("registrada_em", sa.DateTime(timezone=True)),
)
moradores = sa.table(
    "moradores",
    sa.column("id", sa.Integer),
    sa.column("nome", sa.String),
    sa.column("telefone", sa.String),
    sa.column("endereco", sa.String),
    sa.column("corrego_id", sa.Integer),
    sa.column("prioritario", sa.Boolean),
    sa.column("tipo_necessidade", sa.String),
    sa.column("criado_em", sa.DateTime(timezone=True)),
)
alertas = sa.table(
    "alertas",
    sa.column("id", sa.Integer),
    sa.column("corrego_id", sa.Integer),
    sa.column("nivel_risco", sa.String),
    sa.column("mensagem", sa.String),
    sa.column("nivel_agua_cm", sa.Float),
    sa.column("criado_em", sa.DateTime(timezone=True)),
    sa.column("ativo", sa.Boolean),
)


def upgrade() -> None:
    op.bulk_insert(
        corregos,
        [
            {
                "id": 1,
                "nome": "Córrego Ponte Baixa",
                "bairro": "M'Boi Mirim",
                "latitude": -23.6735,
                "longitude": -46.7642,
                "nivel_alerta_cm": 120.0,
                "nivel_critico_cm": 180.0,
            },
            {
                "id": 2,
                "nome": "Córrego Morro do S",
                "bairro": "Campo Limpo",
                "latitude": -23.6489,
                "longitude": -46.7701,
                "nivel_alerta_cm": 100.0,
                "nivel_critico_cm": 150.0,
            },
        ],
    )
    op.bulk_insert(
        sensores,
        [
            {"id": 1, "codigo": "ESP32-PB-01", "corrego_id": 1, "ativo": True,
             "instalado_em": BASE - timedelta(days=30)},
            {"id": 2, "codigo": "ESP32-MS-01", "corrego_id": 2, "ativo": True,
             "instalado_em": BASE - timedelta(days=30)},
        ],
    )
    # Moradores FICTÍCIOS (sem CPF, telefones de exemplo). 3 prioritários.
    op.bulk_insert(
        moradores,
        [
            {"id": 1, "nome": "Dona Benedita (fictícia)", "telefone": "(11) 90000-0001",
             "endereco": "Rua Fictícia das Flores, 10", "corrego_id": 1, "prioritario": True,
             "tipo_necessidade": "IDOSO", "criado_em": BASE - timedelta(days=20)},
            {"id": 2, "nome": "Seu Joaquim (fictício)", "telefone": "(11) 90000-0002",
             "endereco": "Rua Fictícia das Flores, 22", "corrego_id": 1, "prioritario": True,
             "tipo_necessidade": "CADEIRANTE", "criado_em": BASE - timedelta(days=20)},
            {"id": 3, "nome": "Ana Souza (fictícia)", "telefone": "(11) 90000-0003",
             "endereco": "Travessa Exemplo, 5", "corrego_id": 1, "prioritario": False,
             "tipo_necessidade": "NENHUMA", "criado_em": BASE - timedelta(days=19)},
            {"id": 4, "nome": "Dona Cida (fictícia)", "telefone": "(11) 90000-0004",
             "endereco": "Rua Modelo do Morro, 101", "corrego_id": 2, "prioritario": True,
             "tipo_necessidade": "ACAMADO", "criado_em": BASE - timedelta(days=18)},
            {"id": 5, "nome": "Carlos Lima (fictício)", "telefone": "(11) 90000-0005",
             "endereco": "Rua Modelo do Morro, 120", "corrego_id": 2, "prioritario": False,
             "tipo_necessidade": "NENHUMA", "criado_em": BASE - timedelta(days=18)},
            {"id": 6, "nome": "Paula Reis (fictícia)", "telefone": "(11) 90000-0006",
             "endereco": "Viela Teste, 7", "corrego_id": 2, "prioritario": False,
             "tipo_necessidade": "NENHUMA", "criado_em": BASE - timedelta(days=17)},
        ],
    )
    # Ponte Baixa: chuva forte, nível subindo até ALERTA (130 cm >= 120).
    # Morro do S: tempo seco, nível NORMAL.
    op.bulk_insert(
        leituras,
        [
            {"id": 1, "sensor_id": 1, "nivel_agua_cm": 45.0, "chuva_mm_hora": 0.0,
             "registrada_em": BASE - timedelta(hours=3)},
            {"id": 2, "sensor_id": 1, "nivel_agua_cm": 80.0, "chuva_mm_hora": 35.0,
             "registrada_em": BASE - timedelta(hours=2)},
            {"id": 3, "sensor_id": 1, "nivel_agua_cm": 130.0, "chuva_mm_hora": 48.0,
             "registrada_em": BASE - timedelta(hours=1)},
            {"id": 4, "sensor_id": 2, "nivel_agua_cm": 30.0, "chuva_mm_hora": 0.0,
             "registrada_em": BASE - timedelta(hours=2)},
            {"id": 5, "sensor_id": 2, "nivel_agua_cm": 42.0, "chuva_mm_hora": 5.0,
             "registrada_em": BASE - timedelta(hours=1)},
        ],
    )
    op.bulk_insert(
        alertas,
        [
            {"id": 1, "corrego_id": 1, "nivel_risco": "ALERTA",
             "mensagem": "ALERTA: Córrego Ponte Baixa atingiu 130 cm. Prepare-se para sair "
                         "e confirme se os moradores prioritários da sua rua têm ajuda.",
             "nivel_agua_cm": 130.0, "criado_em": BASE - timedelta(hours=1), "ativo": True},
        ],
    )

    # No PostgreSQL, ids explícitos não avançam as sequences: ajusta para evitar conflito.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for tabela in ("corregos", "sensores", "leituras", "moradores", "alertas"):
            op.execute(
                sa.text(
                    f"SELECT setval(pg_get_serial_sequence('{tabela}', 'id'), "
                    f"(SELECT COALESCE(MAX(id), 1) FROM {tabela}))"
                )
            )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM alertas WHERE id IN (1)"))
    op.execute(sa.text("DELETE FROM leituras WHERE id IN (1, 2, 3, 4, 5)"))
    op.execute(sa.text("DELETE FROM moradores WHERE id IN (1, 2, 3, 4, 5, 6)"))
    op.execute(sa.text("DELETE FROM sensores WHERE id IN (1, 2)"))
    op.execute(sa.text("DELETE FROM corregos WHERE id IN (1, 2)"))
