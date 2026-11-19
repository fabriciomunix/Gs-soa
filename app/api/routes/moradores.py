from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.routes._respostas import R404, R422
from app.db.session import get_db
from app.schemas import MoradorCreate, MoradorRead, MoradorUpdate
from app.services.morador_service import MoradorService

router = APIRouter(prefix="/moradores", tags=["Moradores"])


def _service(db: Session = Depends(get_db)) -> MoradorService:
    return MoradorService(db)


@router.get("", response_model=list[MoradorRead], summary="Listar moradores cadastrados")
def listar_moradores(
    corrego_id: int | None = Query(default=None, alias="corregoId", description="Filtra por córrego"),
    service: MoradorService = Depends(_service),
):
    return service.listar(corrego_id)


# Declarada antes de /{morador_id} para não ser capturada pela rota dinâmica.
@router.get(
    "/prioritarios",
    response_model=list[MoradorRead],
    summary="Listar moradores prioritários",
    description="Moradores que precisam de ajuda para sair (idosos, cadeirantes, acamados...).",
    responses={**R404},
)
def listar_prioritarios(
    corrego_id: int | None = Query(default=None, alias="corregoId", description="Filtra por córrego"),
    service: MoradorService = Depends(_service),
):
    return service.listar_prioritarios(corrego_id)


@router.post(
    "",
    response_model=MoradorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar morador",
    description="Moradores com `tipoNecessidade` diferente de NENHUMA são marcados como prioritários.",
    responses={**R404, **R422},
)
def criar_morador(dados: MoradorCreate, service: MoradorService = Depends(_service)):
    return service.criar(dados)


@router.get("/{morador_id}", response_model=MoradorRead, summary="Detalhar morador", responses={**R404})
def obter_morador(morador_id: int, service: MoradorService = Depends(_service)):
    return service.obter(morador_id)


@router.put(
    "/{morador_id}",
    response_model=MoradorRead,
    summary="Atualizar morador",
    description="Atualização parcial: apenas os campos enviados são alterados.",
    responses={**R404, **R422},
)
def atualizar_morador(morador_id: int, dados: MoradorUpdate, service: MoradorService = Depends(_service)):
    return service.atualizar(morador_id, dados)


@router.delete(
    "/{morador_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Remover morador",
    responses={**R404},
)
def remover_morador(morador_id: int, service: MoradorService = Depends(_service)):
    service.remover(morador_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
