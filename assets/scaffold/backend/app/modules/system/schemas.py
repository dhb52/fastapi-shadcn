from typing import Literal

from pydantic import BaseModel


class Health(BaseModel):
    status: Literal["ok"] = "ok"


class AppConfig(BaseModel):
    app_name: str
    environment: str
    captcha_enabled: bool
