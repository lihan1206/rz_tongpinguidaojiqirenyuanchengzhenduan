from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.robot import (
    PositionIn,
    PositionOut,
    RobotCreate,
    RobotOut,
    RobotUpdate,
    StatusLogOut,
)
from app.services.container import get_db, get_robot_service
from app.services.deps import get_current_user
from app.services.rbac import require_permission
from app.services.robot_service import RobotService

router = APIRouter(prefix="/robots", tags=["机器人"])


def get_robot_service_dep(db: Session = Depends(get_db)) -> RobotService:
    return get_robot_service(db)


@router.get("", response_model=list[RobotOut], dependencies=[Depends(require_permission("view"))])
def list_robots(service: RobotService = Depends(get_robot_service_dep), _=Depends(get_current_user)):
    return service.list_all()


@router.post("", response_model=RobotOut, dependencies=[Depends(require_permission("maintenance"))])
def create_robot(
    data: RobotCreate,
    service: RobotService = Depends(get_robot_service_dep),
    _=Depends(get_current_user),
):
    return service.create(data)


@router.get("/{robot_id}", response_model=RobotOut, dependencies=[Depends(require_permission("view"))])
def get_robot(
    robot_id: int,
    service: RobotService = Depends(get_robot_service_dep),
    _=Depends(get_current_user),
):
    return service.get(robot_id)


@router.put("/{robot_id}", response_model=RobotOut, dependencies=[Depends(require_permission("maintenance"))])
def update_robot(
    robot_id: int,
    data: RobotUpdate,
    service: RobotService = Depends(get_robot_service_dep),
    _=Depends(get_current_user),
):
    return service.update(robot_id, data)


@router.delete("/{robot_id}", dependencies=[Depends(require_permission("maintenance"))])
def delete_robot(
    robot_id: int,
    service: RobotService = Depends(get_robot_service_dep),
    _=Depends(get_current_user),
):
    service.delete(robot_id)
    return {"message": "已删除"}


@router.post(
    "/{robot_id}/positions",
    response_model=PositionOut,
    dependencies=[Depends(require_permission("maintenance"))],
)
def report_position(
    robot_id: int,
    data: PositionIn,
    service: RobotService = Depends(get_robot_service_dep),
    _=Depends(get_current_user),
):
    return service.report_position(robot_id, data)


@router.get(
    "/{robot_id}/positions",
    response_model=list[PositionOut],
    dependencies=[Depends(require_permission("view"))],
)
def list_positions(
    robot_id: int,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
    service: RobotService = Depends(get_robot_service_dep),
    _=Depends(get_current_user),
):
    return service.list_positions(robot_id, limit)


@router.get(
    "/{robot_id}/status-logs",
    response_model=list[StatusLogOut],
    dependencies=[Depends(require_permission("view"))],
)
def list_status_logs(
    robot_id: int,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
    service: RobotService = Depends(get_robot_service_dep),
    _=Depends(get_current_user),
):
    return service.list_status_logs(robot_id, limit)
