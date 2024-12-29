from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import PaginatedToDoView, PaginationQuery, ToDo


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "Hello, world!"}


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(todo: ToDo, session: SessionDep) -> ToDo:
    session.add(todo)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"title must be unique ('{todo.title}')",
        )
    session.refresh(todo)
    return todo


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: ToDo, session: SessionDep) -> ToDo:
    statement = select(ToDo).where(ToDo.id == todo_id)
    result = session.exec(statement)
    try:
        updated_todo = result.one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id not found ({todo_id})"
        )
    updated_todo.title = todo.title
    updated_todo.description = todo.description
    session.add(updated_todo)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"title must be unique ('{todo.title}')",
        )
    session.refresh(updated_todo)
    return updated_todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, session: SessionDep) -> None:
    statement = select(ToDo).where(ToDo.id == todo_id)
    result = session.exec(statement)
    try:
        todo = result.one()
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id not found ({todo_id})"
        )
    session.delete(todo)
    session.commit()


@app.get("/todos/", response_model=PaginatedToDoView)
def get_todos(
    pagination_query: Annotated[PaginationQuery, Query()], session: SessionDep
) -> PaginatedToDoView:
    offset = pagination_query.limit * (pagination_query.page - 1)
    statement = select(ToDo).offset(offset).limit(pagination_query.limit)
    todo_list_page = session.exec(statement).all()
    paginated_todo_view = {
        "data": todo_list_page,
        "page": pagination_query.page,
        "limit": pagination_query.limit,
        "total": len(todo_list_page),
    }
    return paginated_todo_view
