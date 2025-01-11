from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel):
    name: str
    email: EmailStr
    password: str


class UserData(SQLModel, table=True):
    name: str
    email: EmailStr = Field(primary_key=True)
    hashed_password: str


class Token(SQLModel):
    token: str


class TokenData(SQLModel):
    email: EmailStr
