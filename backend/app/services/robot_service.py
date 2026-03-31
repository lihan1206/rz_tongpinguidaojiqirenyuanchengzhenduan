from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.robot import Robot, RobotPosition, RobotStatusLog
from app.repositories.robot_repository import RobotRepository
from app.schemas.robot import PositionIn, RobotCreate, RobotUpdate
from app.services.base import BaseService


class RobotService(BaseService[Robot, RobotRepository]):
    def __init__(self, repository: RobotRepository):
        super().__init__(repository)
        self.repository = repository

    def _get_resource_name(self) -> str:
        return "机器人"

    def list_all(self) -> list[Robot]:
        return self.repository.list_all()

    def create(self, data: RobotCreate) -> Robot:
        existing = self.repository.get_by_device_id(data.device_id)
        if existing:
            raise AlreadyExistsException("机器人", "device_id", data.device_id)
        robot = self.repository.create(data.model_dump())
        self.repository.create_status_log(
            robot_id=robot.id,
            from_status=None,
            to_status=robot.status,
            note="创建机器人",
        )
        self.repository.commit()
        return self.repository.refresh(robot)

    def update(self, robot_id: int, data: RobotUpdate) -> Robot:
        robot = self.get(robot_id)
        before_status = robot.status
        update_data = data.model_dump(exclude_unset=True)
        self.repository.update(robot, update_data)
        if data.status is not None and data.status != before_status:
            self.repository.create_status_log(
                robot_id=robot.id,
                from_status=before_status,
                to_status=data.status,
                note="状态变更",
            )
        self.repository.commit()
        return self.repository.refresh(robot)

    def report_position(self, robot_id: int, data: PositionIn) -> RobotPosition:
        self.get(robot_id)
        position = self.repository.create_position(
            robot_id=robot_id,
            lat=data.lat,
            lng=data.lng,
        )
        self.repository.commit()
        return self.repository.refresh(position)

    def list_positions(self, robot_id: int, limit: int = 200) -> list[RobotPosition]:
        self.get(robot_id)
        return self.repository.list_positions(robot_id, limit)

    def list_status_logs(self, robot_id: int, limit: int = 200) -> list[RobotStatusLog]:
        self.get(robot_id)
        return self.repository.list_status_logs(robot_id, limit)
