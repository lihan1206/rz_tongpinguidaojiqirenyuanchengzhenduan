from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.sensor import SensorIn, SensorOut
from app.services.container import get_db, get_sensor_service
from app.services.deps import get_current_user
from app.services.rbac import require_permission
from app.services.sensor_service import SensorService

router = APIRouter(prefix="/sensors", tags=["传感器"])


def get_sensor_service_dep(db: Session = Depends(get_db)) -> SensorService:
    return get_sensor_service(db)


@router.post(
    "/ingest",
    response_model=SensorOut,
    dependencies=[Depends(require_permission("view"))],
)
def ingest(
    data: SensorIn,
    service: SensorService = Depends(get_sensor_service_dep),
    _=Depends(get_current_user),
):
    return service.ingest(data)


@router.get("", response_model=list[SensorOut], dependencies=[Depends(require_permission("view"))])
def list_data(
    robot_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
    service: SensorService = Depends(get_sensor_service_dep),
    _=Depends(get_current_user),
):
    return service.list_data(robot_id, limit)
