from app.db.base import Base
from app.db.session import engine

# 重要：导入所有模型，确保 SQLAlchemy 能注册到 metadata
from app.models import audit  # noqa: F401
from app.models import auth  # noqa: F401
from app.models import command  # noqa: F401
from app.models import diagnosis  # noqa: F401
from app.models import fault  # noqa: F401
from app.models import robot  # noqa: F401
from app.models import sensor  # noqa: F401
from app.models import system  # noqa: F401
from app.models import ticket  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
