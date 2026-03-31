from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.robot import Robot
from app.repositories.base import BaseRepository
from app.schemas.robot import RobotCreate, RobotUpdate


class RobotRepository(BaseRepository[Robot, RobotCreate, RobotUpdate]):
    """机器人Repository"""

    def __init__(self):
        super().__init__(Robot)

    def get_by_sn(self, db: Session, sn: str) -> Optional[Robot]:
        """根据序列号获取机器人"""
        return self.get_by(db, sn=sn)

    def list_by_status(
        self,
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Robot]:
        """按状态获取机器人列表"""
        return self.list(db, status=status, skip=skip, limit=limit)

    def list_online(self, db: Session, skip: int = 0, limit: int = 100) -> List[Robot]:
        """获取在线机器人列表"""
        return self.list_by_status(db, status="online", skip=skip, limit=limit)

    def update_status(self, db: Session, robot_id: int, status: str) -> Optional[Robot]:
        """更新机器人状态"""
        robot = self.get(db, robot_id)
        if robot:
            robot.status = status
            db.commit()
            db.refresh(robot)
        return robot

    def exists_by_sn(self, db: Session, sn: str) -> bool:
        """检查序列号是否存在"""
        return self.exists(db, sn=sn)


# 实例化Repository
robot_repository = RobotRepository()