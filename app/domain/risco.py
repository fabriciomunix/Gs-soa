"""Regras de negócio puras do Alerta Córrego.

Regra de classificação de risco (igual em todas as partes do projeto):
- nível >= nivelCriticoCm                        -> CRITICO
- nível >= nivelAlertaCm                         -> ALERTA
- nível >= 0.75 x nivelAlertaCm OU chuva >= 30   -> ATENCAO
- caso contrário                                 -> NORMAL
"""
from app.domain.enums import NivelRisco, TipoNecessidade

FATOR_ATENCAO = 0.75
CHUVA_ATENCAO_MM_HORA = 30.0
RISCOS_QUE_GERAM_ALERTA = frozenset({NivelRisco.ALERTA, NivelRisco.CRITICO})


def classificar_risco(
    nivel_agua_cm: float,
    chuva_mm_hora: float,
    nivel_alerta_cm: float,
    nivel_critico_cm: float,
) -> NivelRisco:
    """Classifica o risco de transbordamento a partir de uma leitura do sensor."""
    if nivel_agua_cm < 0 or chuva_mm_hora < 0:
        raise ValueError("Nível de água e chuva não podem ser negativos.")
    if nivel_alerta_cm <= 0 or nivel_critico_cm <= nivel_alerta_cm:
        raise ValueError("Limites inválidos: exige 0 < nivelAlertaCm < nivelCriticoCm.")

    if nivel_agua_cm >= nivel_critico_cm:
        return NivelRisco.CRITICO
    if nivel_agua_cm >= nivel_alerta_cm:
        return NivelRisco.ALERTA
    if nivel_agua_cm >= FATOR_ATENCAO * nivel_alerta_cm or chuva_mm_hora >= CHUVA_ATENCAO_MM_HORA:
        return NivelRisco.ATENCAO
    return NivelRisco.NORMAL


def deve_gerar_alerta(risco: NivelRisco) -> bool:
    """Leituras ALERTA ou CRITICO geram um Alerta para o córrego."""
    return risco in RISCOS_QUE_GERAM_ALERTA


def definir_prioridade(tipo_necessidade: TipoNecessidade, prioritario_informado: bool) -> bool:
    """Morador com qualquer necessidade especial é sempre prioritário na evacuação."""
    return prioritario_informado or tipo_necessidade != TipoNecessidade.NENHUMA


def gerar_mensagem_alerta(nome_corrego: str, nivel_agua_cm: float, risco: NivelRisco) -> str:
    """Mensagem amigável exibida no app do morador e no painel web."""
    if risco == NivelRisco.CRITICO:
        return (
            f"RISCO CRÍTICO: {nome_corrego} atingiu {nivel_agua_cm:.0f} cm e pode transbordar "
            "a qualquer momento. Saia agora e ajude vizinhos com mobilidade reduzida."
        )
    if risco == NivelRisco.ALERTA:
        return (
            f"ALERTA: {nome_corrego} atingiu {nivel_agua_cm:.0f} cm. Prepare-se para sair "
            "e confirme se os moradores prioritários da sua rua têm ajuda."
        )
    return f"{nome_corrego}: nível em {nivel_agua_cm:.0f} cm ({risco.value})."
