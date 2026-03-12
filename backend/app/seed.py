import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.command import MaintenanceCommand, RemoteCommand
from app.models.fault import FaultRule
from app.models.robot import Robot, RobotPosition, RobotStatusLog
from app.models.auth import Permission, Role, RolePermission, User, UserRole
from app.models.sensor import SensorData
from app.models.system import SystemConfig
from app.models.ticket import MaintenanceTicket
from app.services.security import hash_password

logger = logging.getLogger(__name__)


def seed_data() -> None:
    init_db()
    db: Session = SessionLocal()
    try:
        _seed_roles_permissions_users(db)
        _seed_configs(db)
        _seed_robots(db)
        _seed_command_templates(db)
        _seed_rules(db)
        _seed_samples(db)
        db.commit()
        logger.info("种子数据已准备完成")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_or_create_role(db: Session, code: str, name: str) -> Role:
    role = db.query(Role).filter(Role.code == code).first()
    if role:
        role.name = name
        return role
    role = Role(code=code, name=name)
    db.add(role)
    db.flush()
    return role


def _get_or_create_permission(db: Session, code: str, name: str) -> Permission:
    p = db.query(Permission).filter(Permission.code == code).first()
    if p:
        p.name = name
        return p
    p = Permission(code=code, name=name)
    db.add(p)
    db.flush()
    return p


def _ensure_role_permission(db: Session, role_id: int, permission_id: int) -> None:
    exists = (
        db.query(RolePermission)
        .filter(RolePermission.role_id == role_id, RolePermission.permission_id == permission_id)
        .first()
    )
    if exists:
        return
    db.add(RolePermission(role_id=role_id, permission_id=permission_id))


def _get_or_create_user(
    db: Session,
    username: str,
    full_name: str,
    password: str,
    phone: str | None = None,
    employee_no: str | None = None,
) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        if not user.password_hash:
            user.password_hash = hash_password(password)
        if not user.full_name:
            user.full_name = full_name
        if phone and not user.phone:
            user.phone = phone
        if employee_no and not user.employee_no:
            user.employee_no = employee_no
        return user
    user = User(
        username=username,
        full_name=full_name,
        password_hash=hash_password(password),
        phone=phone,
        employee_no=employee_no,
        auth_source="local",
    )
    db.add(user)
    db.flush()
    return user


def _ensure_user_role(db: Session, user_id: int, role_id: int) -> None:
    exists = db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).first()
    if exists:
        return
    db.add(UserRole(user_id=user_id, role_id=role_id))


def _seed_roles_permissions_users(db: Session) -> None:
    admin_role = _get_or_create_role(db, "admin", "系统管理员")
    engineer_role = _get_or_create_role(db, "engineer", "运维工程师")
    operator_role = _get_or_create_role(db, "operator", "普通操作员")

    perm_view = _get_or_create_permission(db, "view", "查看")
    perm_diagnose = _get_or_create_permission(db, "diagnose", "诊断")
    perm_remote = _get_or_create_permission(db, "remote_control", "远程控制")
    perm_maint = _get_or_create_permission(db, "maintenance", "维护记录")
    perm_config = _get_or_create_permission(db, "config", "系统配置")
    perm_audit = _get_or_create_permission(db, "audit", "日志审计")

    for p in [perm_view, perm_diagnose, perm_remote, perm_maint, perm_config, perm_audit]:
        _ensure_role_permission(db, admin_role.id, p.id)

    for p in [perm_view, perm_diagnose, perm_remote, perm_maint]:
        _ensure_role_permission(db, engineer_role.id, p.id)

    _ensure_role_permission(db, operator_role.id, perm_view.id)

    admin = _get_or_create_user(db, "admin", "管理员", "123456", phone="13800000000", employee_no="A0001")
    engineer = _get_or_create_user(db, "engineer", "运维工程师", "123456", phone="13900000000", employee_no="E0001")

    _ensure_user_role(db, admin.id, admin_role.id)
    _ensure_user_role(db, engineer.id, engineer_role.id)


def _seed_configs(db: Session) -> None:
    defaults = {
        "采集频率": "5s",
        "报警渠道": "系统",
        "通信协议": "HTTP",
    }
    for k, v in defaults.items():
        row = db.query(SystemConfig).filter(SystemConfig.key == k).first()
        if row:
            continue
        db.add(SystemConfig(key=k, value=v))


def _seed_robots(db: Session) -> None:
    if db.query(Robot).count() > 0:
        return

    robots = [
        Robot(device_id="TC-RB-0001", model="TC-Track-A1", location="A区-1号线", status="运行中", ip="10.0.0.11", port=9001),
        Robot(device_id="TC-RB-0002", model="TC-Track-A1", location="A区-2号线", status="在线", ip="10.0.0.12", port=9001),
        Robot(device_id="TC-RB-0003", model="TC-Track-B2", location="B区-仓储线", status="离线", ip="10.0.0.13", port=9001),
    ]
    db.add_all(robots)
    db.flush()

    for r in robots:
        db.add(RobotStatusLog(robot_id=r.id, from_status=None, to_status=r.status, note="初始化"))

    db.add_all(
        [
            RobotPosition(robot_id=robots[0].id, lat=31.230416, lng=121.473701),
            RobotPosition(robot_id=robots[1].id, lat=31.229000, lng=121.480000),
        ]
    )


def _seed_command_templates(db: Session) -> None:
    if db.query(MaintenanceCommand).count() > 0:
        return

    db.add_all(
        [
            MaintenanceCommand(name="重启设备", command_type="重启", default_params_json="{}"),
            MaintenanceCommand(name="复位设备", command_type="复位", default_params_json="{}"),
            MaintenanceCommand(name="模式切换", command_type="模式切换", default_params_json='{"mode":"巡检"}'),
        ]
    )


def _seed_rules(db: Session) -> None:
    if db.query(FaultRule).count() > 0:
        return

    db.add_all(
        [
            FaultRule(name="温度过高", sensor_type="温度", operator=">", threshold=80, level="紧急", enabled=True),
            FaultRule(name="电压过低", sensor_type="电压", operator="<", threshold=20, level="严重", enabled=True),
        ]
    )


def _seed_samples(db: Session) -> None:
    if db.query(SensorData).count() == 0:
        db.add_all(
            [
                SensorData(robot_id=1, sensor_type="温度", value=Decimal("62.1")),
                SensorData(robot_id=1, sensor_type="温度", value=Decimal("78.3")),
                SensorData(robot_id=2, sensor_type="电压", value=Decimal("24.2")),
                SensorData(robot_id=2, sensor_type="电压", value=Decimal("19.7")),
            ]
        )

    if db.query(MaintenanceTicket).count() == 0:
        db.add(
            MaintenanceTicket(robot_id=2, title="更换电池", description="电压波动，建议检查电池健康度", status="待处理")
        )

    if db.query(RemoteCommand).count() == 0:
        db.add(RemoteCommand(robot_id=1, command_type="重启", params_json="{}", status="成功", result="已完成"))
