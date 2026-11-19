from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.routes._respostas import R404, R409
from app.db.session import get_db
from app.schemas import AlertaRead
from app.services.alerta_service import AlertaService

router = APIRouter(prefix="/alertas", tags=["Alertas"])


def _service(db: Session = Depends(get_db)) -> AlertaService:
    return AlertaService(db)


@router.get("", response_model=list[AlertaRead], summary="Listar alertas")
def listar_alertas(
    ativos: bool | None = Query(default=None, description="true = só ativos; false = só encerrados"),
    corrego_id: int | None = Query(default=None, alias="corregoId", description="Filtra por córrego"),
    service: AlertaService = Depends(_service),
):
    return service.listar(ativos=ativos, corrego_id=corrego_id)


@router.patch(
    "/{alerta_id}/encerrar",
    response_model=AlertaRead,
    summary="Encerrar alerta",
    description="Marca o alerta como inativo (a água baixou / situação controlada).",
    responses={**R404, **R409},
)
def encerrar_alerta(alerta_id: int, service: AlertaService = Depends(_service)):
    return service.encerrar(alerta_id)
