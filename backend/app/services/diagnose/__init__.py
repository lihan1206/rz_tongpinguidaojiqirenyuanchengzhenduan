# 使用延迟导入避免在导入包时就需要数据库依赖
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.diagnose.diagnose_service import DiagnoseService
    from app.services.diagnose.strategy_factory import DiagnoseStrategyFactory

__all__ = [
    "DiagnoseService",
    "DiagnoseStrategyFactory",
    "diagnose_service",
    "strategy_factory",
]

def __getattr__(name):
    """延迟导入"""
    if name == "diagnose_service":
        from app.services.diagnose.diagnose_service import diagnose_service
        return diagnose_service
    if name == "DiagnoseService":
        from app.services.diagnose.diagnose_service import DiagnoseService
        return DiagnoseService
    if name == "strategy_factory":
        from app.services.diagnose.strategy_factory import strategy_factory
        return strategy_factory
    if name == "DiagnoseStrategyFactory":
        from app.services.diagnose.strategy_factory import DiagnoseStrategyFactory
        return DiagnoseStrategyFactory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")