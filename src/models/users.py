from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    name: str
    email: EmailStr = Field(primary_key=True)
    password: str


class Token(SQLModel):
    token: str


class TokenData(SQLModel):
    email: EmailStr
