from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.system import SystemConfig
from app.schemas.system import ConfigOut, ConfigUpsert
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/configs", tags=["系统配置"])


@router.get("", response_model=list[ConfigOut], dependencies=[Depends(require_permission("config"))])
def list_configs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(SystemConfig).order_by(SystemConfig.key.asc()).all()


@router.post("", response_model=ConfigOut, dependencies=[Depends(require_permission("config"))])
def upsert_config(data: ConfigUpsert, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(SystemConfig).filter(SystemConfig.key == data.key).first()
    if row:
        row.value = data.value
    else:
        row = SystemConfig(key=data.key, value=data.value)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row
