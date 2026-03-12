from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.fault import AlarmNotification, FaultLog, FaultRule
from app.models.sensor import SensorData
from app.schemas.sensor import SensorIn, SensorOut
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/sensors", tags=["传感器"])


def _rule_hit(operator: str, value: float, threshold: float) -> bool:
    if operator == ">":
        return value > threshold
    if operator == ">=":
        return value >= threshold
    if operator == "<":
        return value < threshold
    if operator == "<=":
        return value <= threshold
    if operator == "==":
        return value == threshold
    return False


@router.post(
    "/ingest",
    response_model=SensorOut,
    dependencies=[Depends(require_permission("view"))],
)
def ingest(data: SensorIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = SensorData(robot_id=data.robot_id, sensor_type=data.sensor_type, value=data.value)
    db.add(row)
    db.flush()

    rules = (
        db.query(FaultRule)
        .filter(FaultRule.enabled.is_(True), FaultRule.sensor_type == data.sensor_type)
        .all()
    )
    for rule in rules:
        if _rule_hit(rule.operator, float(data.value), float(rule.threshold)):
            log = FaultLog(
                robot_id=data.robot_id,
                rule_id=rule.id,
                fault_type=rule.name,
                description=f"传感器[{data.sensor_type}]数值为{data.value}，触发规则：{rule.operator}{rule.threshold}",
                level=rule.level,
            )
            db.add(log)
            db.flush()
            db.add(
                AlarmNotification(
                    fault_log_id=log.id,
                    channel="系统",
                    content=f"机器人#{data.robot_id}触发告警：{log.description}",
                )
            )

    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[SensorOut], dependencies=[Depends(require_permission("view"))])
def list_data(robot_id: int | None = None, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(SensorData).order_by(SensorData.id.desc())
    if robot_id is not None:
        q = q.filter(SensorData.robot_id == robot_id)
    return q.limit(min(limit, 500)).all()
