import base64
import hashlib
import hmac
import secrets
from io import BytesIO

from captcha.image import ImageCaptcha
from fastapi import HTTPException
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings

CAPTCHA_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CAPTCHA_LENGTH = 5
CAPTCHA_SALT = "captcha-v1"


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt=CAPTCHA_SALT)


def _digest(answer: str) -> str:
    normalized = answer.strip().upper().encode("utf-8")
    return hmac.new(settings.secret_key.encode("utf-8"), normalized, hashlib.sha256).hexdigest()


def issue_captcha_token(answer: str) -> str:
    return _serializer().dumps({"d": _digest(answer)})


def verify_captcha_token(token: str, answer: str) -> bool:
    try:
        payload = _serializer().loads(token, max_age=settings.captcha_ttl_seconds)
    except (BadSignature, SignatureExpired):
        return False
    expected = payload.get("d") if isinstance(payload, dict) else None
    return isinstance(expected, str) and hmac.compare_digest(expected, _digest(answer))


def generate_captcha() -> tuple[str, str]:
    answer = "".join(secrets.choice(CAPTCHA_ALPHABET) for _ in range(CAPTCHA_LENGTH))
    image = ImageCaptcha(width=180, height=60).generate(answer)
    if not isinstance(image, BytesIO):
        image = BytesIO(image)
    encoded = base64.b64encode(image.getvalue()).decode("ascii")
    return answer, f"data:image/png;base64,{encoded}"


def verify_captcha_or_raise(token: str, answer: str) -> None:
    if not settings.captcha_enabled:
        return
    if not verify_captcha_token(token, answer):
        raise HTTPException(status_code=400, detail="Invalid or expired captcha")
