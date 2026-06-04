from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="A valid email address to register")
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long"
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Register user email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token string")
    token_type: str = Field("bearer", description="Token style classification")


class UserResponse(BaseModel):
    id: str = Field(..., description="Unique UUID for the user")
    email: str = Field(..., description="User email address")
