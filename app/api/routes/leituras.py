from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.routes._respostas import R404, R422
from app.db.session import get_db
from app.schemas import LeituraCreate, LeituraRead, LeituraRegistrada
from app.services.leitura_service import LeituraService

router = APIRouter(prefix="/leituras", tags=["Leituras"])


def _service(db: Session = Depends(get_db)) -> LeituraService:
    return LeituraService(db)


@router.post(
    "",
    response_model=LeituraRegistrada,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar leitura do sensor",
    description=(
        "Endpoint chamado pelo ESP32. Classifica o risco "
        "(NORMAL / ATENCAO / ALERTA / CRITICO) com base nos limites do córrego. "
        "Se o risco for **ALERTA** ou **CRITICO**, cria um Alerta e devolve a lista de "
        "moradores prioritários (idosos, cadeirantes, acamados) do córrego."
    ),
    responses={**R404, **R422},
)
def registrar_leitura(dados: LeituraCreate, service: LeituraService = Depends(_service)):
    return service.registrar(dados)


@router.get("", response_model=list[LeituraRead], summary="Listar leituras recentes", responses={**R404})
def listar_leituras(
    corrego_id: int | None = Query(default=None, alias="corregoId", description="Filtra por córrego"),
    limite: int = Query(default=50, ge=1, le=500, description="Quantidade máxima de leituras"),
    service: LeituraService = Depends(_service),
):
    return service.listar(corrego_id=corrego_id, limite=limite)
