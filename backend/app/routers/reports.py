from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.command import RemoteCommand
from app.models.fault import FaultLog
from app.models.robot import Robot
from app.models.sensor import SensorData
from app.models.ticket import MaintenanceTicket
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/reports", tags=["报表"])


@router.get("/overview", dependencies=[Depends(require_permission("view"))])
def overview(db: Session = Depends(get_db), _=Depends(get_current_user)):
    robots = db.query(func.count(Robot.id)).scalar() or 0
    faults = db.query(func.count(FaultLog.id)).scalar() or 0
    tickets = db.query(func.count(MaintenanceTicket.id)).scalar() or 0
    commands = db.query(func.count(RemoteCommand.id)).scalar() or 0
    sensor_rows = db.query(func.count(SensorData.id)).scalar() or 0

    return {
        "robots": robots,
        "faults": faults,
        "tickets": tickets,
        "commands": commands,
        "sensor_rows": sensor_rows,
    }
