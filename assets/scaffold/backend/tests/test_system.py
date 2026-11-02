from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_config_reports_captcha_flag(client: AsyncClient) -> None:
    response = await client.get("/api/v1/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["app_name"] == "FastAPI + shadcn"
    assert payload["environment"] == "development"
    assert payload["captcha_enabled"] is False
