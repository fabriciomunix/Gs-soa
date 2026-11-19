from datetime import datetime

from pydantic import Field

from app.domain.enums import TipoNecessidade
from app.schemas.base import CamelModel

# Aceita (11) 91234-5678, 11912345678, 11 1234-5678 ...
PADRAO_TELEFONE = r"^\(?\d{2}\)?\s?9?\d{4}-?\d{4}$"


class MoradorCreate(CamelModel):
    nome: str = Field(min_length=3, max_length=120, examples=["Maria (fictícia)"])
    telefone: str = Field(pattern=PADRAO_TELEFONE, examples=["(11) 90000-0001"])
    endereco: str = Field(min_length=5, max_length=200, examples=["Rua Fictícia, 100"])
    corrego_id: int = Field(gt=0, examples=[1])
    prioritario: bool = False
    tipo_necessidade: TipoNecessidade = TipoNecessidade.NENHUMA


class MoradorUpdate(CamelModel):
    """Atualização parcial: envie apenas os campos que deseja alterar."""

    nome: str | None = Field(default=None, min_length=3, max_length=120)
    telefone: str | None = Field(default=None, pattern=PADRAO_TELEFONE)
    endereco: str | None = Field(default=None, min_length=5, max_length=200)
    corrego_id: int | None = Field(default=None, gt=0)
    prioritario: bool | None = None
    tipo_necessidade: TipoNecessidade | None = None


class MoradorRead(CamelModel):
    id: int
    nome: str
    telefone: str
    endereco: str
    corrego_id: int
    prioritario: bool
    tipo_necessidade: TipoNecessidade
    criado_em: datetime


class MoradorResumo(CamelModel):
    """Dados mínimos para a equipe/vizinhos ajudarem na evacuação."""

    id: int
    nome: str
    telefone: str
    endereco: str
    tipo_necessidade: TipoNecessidade
