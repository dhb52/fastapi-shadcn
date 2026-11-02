from fastapi import APIRouter

from app.core.config import settings
from app.modules.system.schemas import AppConfig, Health

router = APIRouter(tags=["system"])


@router.get("/health", response_model=Health)
async def health() -> Health:
    return Health()


@router.get("/config", response_model=AppConfig)
async def read_config() -> AppConfig:
    return AppConfig(
        app_name=settings.app_name,
        environment=settings.environment,
        captcha_enabled=settings.captcha_enabled,
    )
