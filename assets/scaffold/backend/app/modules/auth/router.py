from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import settings
from app.core.limiter import limiter
from app.modules.auth.captcha import (
    generate_captcha,
    issue_captcha_token,
    verify_captcha_or_raise,
)
from app.modules.auth.schemas import (
    CaptchaChallenge,
    CaptchaVerification,
    CaptchaVerifyRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/captcha", response_model=CaptchaChallenge)
@limiter.limit("10/minute")
def get_captcha(request: Request, response: Response) -> CaptchaChallenge:
    if not settings.captcha_enabled:
        raise HTTPException(status_code=404, detail="Captcha is disabled")
    answer, image = generate_captcha()
    return CaptchaChallenge(token=issue_captcha_token(answer), image=image)


@router.post("/captcha/verify", response_model=CaptchaVerification)
@limiter.limit("20/minute")
def verify_captcha(
    payload: CaptchaVerifyRequest,
    request: Request,
    response: Response,
) -> CaptchaVerification:
    if not settings.captcha_enabled:
        raise HTTPException(status_code=404, detail="Captcha is disabled")
    verify_captcha_or_raise(payload.token, payload.code)
    return CaptchaVerification(valid=True)
