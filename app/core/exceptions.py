"""Exceções de negócio, traduzidas para HTTP em app/main.py."""


class ErroDeNegocio(Exception):
    """Base das exceções da camada de serviço."""

    status_code = 400

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class RecursoNaoEncontrado(ErroDeNegocio):
    status_code = 404


class RegraNegocioViolada(ErroDeNegocio):
    status_code = 422


class ConflitoDeDados(ErroDeNegocio):
    status_code = 409
