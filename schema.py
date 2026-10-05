# schema.py
from pydantic import BaseModel, ConfigDict, Field, field_validator

def _clean(value: str, lower=False, upper=False) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Must not be empty")
    if lower:
        value = value.lower()
    if upper:
        value = value.upper()
    return value

class CreateAccountSchema(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=30)
    user_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=72)


class CreateAccountResponse(BaseModel):
    status: bool
    message: str


class LoginAccountSchema(BaseModel):
    user_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ProfileResponse(BaseModel):
    message: str
    user_id: str
    name: str

class MessageResponse(BaseModel):
    status: bool
    message: str

class PartConfigSchema(BaseModel):
    part: str = Field(..., min_length=1, max_length=50)
    km_life: int = Field(..., gt=0)
    month_life: int = Field(..., gt=0)
    km_limit: int = Field(..., ge=0)
    day_limit: int = Field(..., ge=0)

    @field_validator("part")
    @classmethod
    def clean_part(cls, v):
        return _clean(v, lower=True)


class PartUpdateSchema(BaseModel):
    km_life: int = Field(..., gt=0)
    month_life: int = Field(..., gt=0)
    km_limit: int = Field(..., ge=0)
    day_limit: int = Field(..., ge=0)


class PartConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    part: str
    km_life: int
    month_life: int
    km_limit: int
    day_limit: int
