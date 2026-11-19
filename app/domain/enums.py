"""Enumerações do domínio (mesmos nomes usados no Mobile e no C#)."""
from enum import Enum


class NivelRisco(str, Enum):
    NORMAL = "NORMAL"
    ATENCAO = "ATENCAO"
    ALERTA = "ALERTA"
    CRITICO = "CRITICO"


class TipoNecessidade(str, Enum):
    NENHUMA = "NENHUMA"
    IDOSO = "IDOSO"
    CADEIRANTE = "CADEIRANTE"
    ACAMADO = "ACAMADO"
    OUTRA = "OUTRA"
