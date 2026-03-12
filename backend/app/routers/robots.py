from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.robot import Robot, RobotPosition, RobotStatusLog
from app.schemas.robot import PositionIn, PositionOut, RobotCreate, RobotOut, RobotUpdate, StatusLogOut
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/robots", tags=["机器人"])


@router.get("", response_model=list[RobotOut], dependencies=[Depends(require_permission("view"))])
def list_robots(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Robot).order_by(Robot.id.desc()).all()


@router.post("", response_model=RobotOut, dependencies=[Depends(require_permission("maintenance"))])
def create_robot(data: RobotCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    exists = db.query(Robot).filter(Robot.device_id == data.device_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="设备ID已存在")
    robot = Robot(**data.model_dump())
    db.add(robot)
    db.flush()
    db.add(RobotStatusLog(robot_id=robot.id, from_status=None, to_status=robot.status, note="创建机器人"))
    db.commit()
    db.refresh(robot)
    return robot


@router.get("/{robot_id}", response_model=RobotOut, dependencies=[Depends(require_permission("view"))])
def get_robot(robot_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    robot = db.get(Robot, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="机器人不存在")
    return robot


@router.put("/{robot_id}", response_model=RobotOut, dependencies=[Depends(require_permission("maintenance"))])
def update_robot(robot_id: int, data: RobotUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    robot = db.get(Robot, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="机器人不存在")

    before_status = robot.status
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(robot, k, v)

    if data.status is not None and data.status != before_status:
        db.add(
            RobotStatusLog(
                robot_id=robot.id,
                from_status=before_status,
                to_status=data.status,
                note="状态变更",
            )
        )

    db.commit()
    db.refresh(robot)
    return robot


@router.delete("/{robot_id}", dependencies=[Depends(require_permission("maintenance"))])
def delete_robot(robot_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    robot = db.get(Robot, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="机器人不存在")
    db.delete(robot)
    db.commit()
    return {"message": "已删除"}


@router.post(
    "/{robot_id}/positions",
    response_model=PositionOut,
    dependencies=[Depends(require_permission("maintenance"))],
)
def report_position(robot_id: int, data: PositionIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    robot = db.get(Robot, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="机器人不存在")
    row = RobotPosition(robot_id=robot_id, lat=data.lat, lng=data.lng)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get(
    "/{robot_id}/positions",
    response_model=list[PositionOut],
    dependencies=[Depends(require_permission("view"))],
)
def list_positions(robot_id: int, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return (
        db.query(RobotPosition)
        .filter(RobotPosition.robot_id == robot_id)
        .order_by(RobotPosition.id.desc())
        .limit(min(limit, 500))
        .all()
    )


@router.get(
    "/{robot_id}/status-logs",
    response_model=list[StatusLogOut],
    dependencies=[Depends(require_permission("view"))],
)
def list_status_logs(robot_id: int, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return (
        db.query(RobotStatusLog)
        .filter(RobotStatusLog.robot_id == robot_id)
        .order_by(RobotStatusLog.id.desc())
        .limit(min(limit, 500))
        .all()
    )
