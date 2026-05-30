"""Auth DTOs."""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    name: str
    role: str
    facility_id: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOut | None = None
