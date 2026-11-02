from httpx import AsyncClient

from app.modules.auth.captcha import issue_captcha_token, verify_captcha_token


def test_captcha_token_is_case_insensitive() -> None:
    token = issue_captcha_token("ABC12")
    assert verify_captcha_token(token, "abc12") is True
    assert verify_captcha_token(token, "wrong") is False


def test_captcha_token_does_not_contain_answer() -> None:
    token = issue_captcha_token("ABC12")
    assert "ABC12" not in token


async def test_captcha_endpoint_is_disabled_by_default(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/captcha")
    assert response.status_code == 404
