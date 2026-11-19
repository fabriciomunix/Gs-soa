from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.routes._respostas import R404, R422
from app.db.session import get_db
from app.schemas import CorregoCreate, CorregoRead, CorregoStatus, CorregoUpdate
from app.services.corrego_service import CorregoService

router = APIRouter(prefix="/corregos", tags=["Córregos"])


def _service(db: Session = Depends(get_db)) -> CorregoService:
    return CorregoService(db)


@router.get("", response_model=list[CorregoRead], summary="Listar córregos monitorados")
def listar_corregos(service: CorregoService = Depends(_service)):
    return service.listar()


@router.post(
    "",
    response_model=CorregoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar córrego",
    description="Cadastra um córrego com seus limites de alerta e crítico (cm). "
    "`nivelCriticoCm` precisa ser maior que `nivelAlertaCm`.",
    responses={**R422},
)
def criar_corrego(dados: CorregoCreate, service: CorregoService = Depends(_service)):
    return service.criar(dados)


@router.get("/{corrego_id}", response_model=CorregoRead, summary="Detalhar córrego", responses={**R404})
def obter_corrego(corrego_id: int, service: CorregoService = Depends(_service)):
    return service.obter(corrego_id)


@router.put(
    "/{corrego_id}",
    response_model=CorregoRead,
    summary="Atualizar córrego",
    description="Atualização parcial: apenas os campos enviados são alterados.",
    responses={**R404, **R422},
)
def atualizar_corrego(corrego_id: int, dados: CorregoUpdate, service: CorregoService = Depends(_service)):
    return service.atualizar(corrego_id, dados)


@router.delete(
    "/{corrego_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Remover córrego",
    description="Remove o córrego e, em cascata, seus sensores, leituras, moradores e alertas.",
    responses={**R404},
)
def remover_corrego(corrego_id: int, service: CorregoService = Depends(_service)):
    service.remover(corrego_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{corrego_id}/status",
    response_model=CorregoStatus,
    summary="Status atual do córrego",
    description="Último nível de água, chuva, nível de risco calculado e última leitura. "
    "Usado pela tela inicial do app do morador.",
    responses={**R404},
)
def status_corrego(corrego_id: int, service: CorregoService = Depends(_service)):
    return service.status(corrego_id)
