from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class ToDo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str = Field(unique=True)
    description: str


class PaginationQuery(BaseModel):
    page: Optional[int] = Field(default=1, gt=0, le=20)
    limit: Optional[int] = Field(default=10, ge=0, le=20)


class PaginatedToDoView(BaseModel):
    data: list[ToDo]
    page: int
    limit: int
    total: int = Field(ge=0, le=20)
