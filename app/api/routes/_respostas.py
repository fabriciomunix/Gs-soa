"""Respostas de erro documentadas no Swagger."""
from app.schemas.base import ErroResposta

R404 = {404: {"model": ErroResposta, "description": "Recurso não encontrado"}}
R409 = {409: {"model": ErroResposta, "description": "Conflito com o estado atual"}}
R422 = {422: {"description": "Dados inválidos ou regra de negócio violada"}}
