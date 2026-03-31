import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.models.audit import OperationLog
from app.routers import (
    admin,
    audits,
    auth,
    commands,
    configs,
    diagnosis,
    faults,
    reports,
    robots,
    sensors,
    tickets,
)

setup_logging(settings.app_name)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="0.1.0")

if settings.cors_allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class OperationLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        if request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            user_id = None
            auth_header = request.headers.get("authorization") or ""
            # 不在中间件做强鉴权，仅用于审计记录
            if auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1].strip()
                # 延迟导入，避免启动时循环依赖
                from jose import JWTError, jwt

                try:
                    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
                    sub = payload.get("sub")
                    if sub:
                        user_id = int(sub)
                except (JWTError, ValueError):
                    user_id = None

            db = SessionLocal()
            try:
                db.add(
                    OperationLog(
                        user_id=user_id,
                        method=request.method.upper(),
                        path=str(request.url.path),
                        summary=None,
                    )
                )
                db.commit()
            except Exception:
                db.rollback()
                logger.exception("写入操作审计失败")
            finally:
                db.close()

        return response


app.add_middleware(OperationLogMiddleware)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api")
app.include_router(robots.router, prefix="/api")
app.include_router(sensors.router, prefix="/api")
app.include_router(diagnosis.router, prefix="/api")
app.include_router(faults.router, prefix="/api")
app.include_router(commands.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(configs.router, prefix="/api")
app.include_router(audits.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
