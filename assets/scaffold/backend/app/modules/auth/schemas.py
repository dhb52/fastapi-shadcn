from pydantic import BaseModel, Field


class CaptchaChallenge(BaseModel):
    token: str
    image: str


class CaptchaVerifyRequest(BaseModel):
    token: str = Field(min_length=1)
    code: str = Field(min_length=1, max_length=8)


class CaptchaVerification(BaseModel):
    valid: bool
