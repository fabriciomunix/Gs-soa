"""Testes da regra pura de domínio (não dependem de FastAPI nem de banco)."""
import pytest

from app.domain import (
    NivelRisco,
    TipoNecessidade,
    classificar_risco,
    definir_prioridade,
    deve_gerar_alerta,
    gerar_mensagem_alerta,
)

ALERTA = 120.0
CRITICO = 180.0


def risco(nivel: float, chuva: float = 0.0) -> NivelRisco:
    return classificar_risco(nivel, chuva, ALERTA, CRITICO)


def test_normal():
    assert risco(50) == NivelRisco.NORMAL


def test_atencao_por_nivel():
    assert risco(100) == NivelRisco.ATENCAO


def test_atencao_por_chuva_mesmo_com_nivel_baixo():
    assert risco(10, chuva=35) == NivelRisco.ATENCAO


def test_alerta():
    assert risco(150) == NivelRisco.ALERTA


def test_critico():
    assert risco(200) == NivelRisco.CRITICO


@pytest.mark.parametrize(
    ("nivel", "chuva", "esperado"),
    [
        (89.99, 0, NivelRisco.NORMAL),     # logo abaixo de 0.75 x 120 = 90
        (90.0, 0, NivelRisco.ATENCAO),     # exatamente 75% do alerta
        (0, 29.99, NivelRisco.NORMAL),     # chuva logo abaixo de 30
        (0, 30.0, NivelRisco.ATENCAO),     # chuva exatamente 30 mm/h
        (119.99, 0, NivelRisco.ATENCAO),
        (120.0, 0, NivelRisco.ALERTA),     # exatamente no nível de alerta
        (179.99, 100, NivelRisco.ALERTA),  # chuva forte não eleva acima de ALERTA
        (180.0, 0, NivelRisco.CRITICO),    # exatamente no nível crítico
    ],
)
def test_limites(nivel, chuva, esperado):
    assert risco(nivel, chuva) == esperado


@pytest.mark.parametrize(
    ("nivel", "chuva", "alerta", "critico"),
    [(-1, 0, 120, 180), (10, -1, 120, 180), (10, 0, 0, 180), (10, 0, 180, 120)],
)
def test_entradas_invalidas(nivel, chuva, alerta, critico):
    with pytest.raises(ValueError):
        classificar_risco(nivel, chuva, alerta, critico)


@pytest.mark.parametrize(
    ("nivel_risco", "gera"),
    [
        (NivelRisco.NORMAL, False),
        (NivelRisco.ATENCAO, False),
        (NivelRisco.ALERTA, True),
        (NivelRisco.CRITICO, True),
    ],
)
def test_deve_gerar_alerta(nivel_risco, gera):
    assert deve_gerar_alerta(nivel_risco) is gera


def test_prioridade_por_necessidade():
    assert definir_prioridade(TipoNecessidade.CADEIRANTE, False) is True
    assert definir_prioridade(TipoNecessidade.NENHUMA, False) is False
    assert definir_prioridade(TipoNecessidade.NENHUMA, True) is True


def test_mensagem_critica_cita_corrego_e_nivel():
    msg = gerar_mensagem_alerta("Córrego Ponte Baixa", 185, NivelRisco.CRITICO)
    assert "Córrego Ponte Baixa" in msg
    assert "185" in msg
    assert "CRÍTICO" in msg
