"""Cria as tabelas do domínio Alerta Córrego.

Revision ID: 0001_criar_tabelas
Revises:
Create Date: 2026-11-19
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_criar_tabelas"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "corregos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("bairro", sa.String(length=120), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("nivel_alerta_cm", sa.Float(), nullable=False),
        sa.Column("nivel_critico_cm", sa.Float(), nullable=False),
        sa.CheckConstraint("nivel_critico_cm > nivel_alerta_cm", name="ck_corregos_limites"),
    )

    op.create_table(
        "sensores",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column(
            "corrego_id",
            sa.Integer(),
            sa.ForeignKey("corregos.id", ondelete="CASCADE", name="fk_sensores_corrego"),
            nullable=False,
        ),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("instalado_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sensores_codigo", "sensores", ["codigo"], unique=True)
    op.create_index("ix_sensores_corrego_id", "sensores", ["corrego_id"])

    op.create_table(
        "leituras",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "sensor_id",
            sa.Integer(),
            sa.ForeignKey("sensores.id", ondelete="CASCADE", name="fk_leituras_sensor"),
            nullable=False,
        ),
        sa.Column("nivel_agua_cm", sa.Float(), nullable=False),
        sa.Column("chuva_mm_hora", sa.Float(), nullable=False, server_default="0"),
        sa.Column("registrada_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_leituras_sensor_id", "leituras", ["sensor_id"])
    op.create_index("ix_leituras_registrada_em", "leituras", ["registrada_em"])

    op.create_table(
        "moradores",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("telefone", sa.String(length=20), nullable=False),
        sa.Column("endereco", sa.String(length=200), nullable=False),
        sa.Column(
            "corrego_id",
            sa.Integer(),
            sa.ForeignKey("corregos.id", ondelete="CASCADE", name="fk_moradores_corrego"),
            nullable=False,
        ),
        sa.Column("prioritario", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "tipo_necessidade", sa.String(length=20), nullable=False, server_default="NENHUMA"
        ),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_moradores_corrego_id", "moradores", ["corrego_id"])

    op.create_table(
        "alertas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "corrego_id",
            sa.Integer(),
            sa.ForeignKey("corregos.id", ondelete="CASCADE", name="fk_alertas_corrego"),
            nullable=False,
        ),
        sa.Column("nivel_risco", sa.String(length=20), nullable=False),
        sa.Column("mensagem", sa.String(length=500), nullable=False),
        sa.Column("nivel_agua_cm", sa.Float(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_alertas_corrego_id", "alertas", ["corrego_id"])
    op.create_index("ix_alertas_criado_em", "alertas", ["criado_em"])
    op.create_index("ix_alertas_ativo", "alertas", ["ativo"])


def downgrade() -> None:
    op.drop_index("ix_alertas_ativo", table_name="alertas")
    op.drop_index("ix_alertas_criado_em", table_name="alertas")
    op.drop_index("ix_alertas_corrego_id", table_name="alertas")
    op.drop_table("alertas")
    op.drop_index("ix_moradores_corrego_id", table_name="moradores")
    op.drop_table("moradores")
    op.drop_index("ix_leituras_registrada_em", table_name="leituras")
    op.drop_index("ix_leituras_sensor_id", table_name="leituras")
    op.drop_table("leituras")
    op.drop_index("ix_sensores_corrego_id", table_name="sensores")
    op.drop_index("ix_sensores_codigo", table_name="sensores")
    op.drop_table("sensores")
    op.drop_table("corregos")
