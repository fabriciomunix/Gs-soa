from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.routes._respostas import R404, R409, R422
from app.db.session import get_db
from app.schemas import SensorCreate, SensorRead
from app.services.sensor_service import SensorService

router = APIRouter(prefix="/sensores", tags=["Sensores"])


def _service(db: Session = Depends(get_db)) -> SensorService:
    return SensorService(db)


@router.get("", response_model=list[SensorRead], summary="Listar sensores")
def listar_sensores(
    corrego_id: int | None = Query(default=None, alias="corregoId", description="Filtra por córrego"),
    service: SensorService = Depends(_service),
):
    return service.listar(corrego_id)


@router.post(
    "",
    response_model=SensorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar sensor (ESP32)",
    responses={**R404, **R409, **R422},
)
def criar_sensor(dados: SensorCreate, service: SensorService = Depends(_service)):
    return service.criar(dados)


@router.get("/{sensor_id}", response_model=SensorRead, summary="Detalhar sensor", responses={**R404})
def obter_sensor(sensor_id: int, service: SensorService = Depends(_service)):
    return service.obter(sensor_id)
