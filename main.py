from typing import Annotated, Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

import utils


TODO_SQL_DB = "todos.db"

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello, world!"}


class ToDoID(BaseModel):
    id: int


class ToDo(BaseModel):
    title: str
    description: str


class ToDoListItem(ToDo, ToDoID):
    pass


@app.post("/todos", response_model=ToDoListItem, status_code=status.HTTP_201_CREATED)
def create_todo(todo: ToDo):
    insert_query = "INSERT INTO todos(title, description) VALUES (?, ?) RETURNING *;"
    params = (todo.title, todo.description)
    result = utils.execute_query(TODO_SQL_DB, insert_query, params, commit=True, return_value=True)
    todo_id, title, description = result[0]
    todo_list_item = {
        "id": todo_id,
        "title": title,
        "description": description
    }
    return todo_list_item


@app.put("/todos/{todo_id}", response_model=ToDoListItem)
def update_todo(todo_id: int, todo: ToDo):
    update_query = "UPDATE todos SET title = ?, description = ? WHERE id = ? RETURNING *;"
    params = (todo.title, todo.description, todo_id)
    result = utils.execute_query(TODO_SQL_DB, update_query, params, commit=True, return_value=True)
    todo_id, title, description = result[0]
    todo_list_item = {
        "id": todo_id,
        "title": title,
        "description": description
    }
    return todo_list_item


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    delete_query = "DELETE FROM todos WHERE id = ?;"
    params = (todo_id,)
    utils.execute_query(TODO_SQL_DB, delete_query, params, commit=True)


class PaginationQuery(BaseModel):
    page: Optional[int] = 1
    limit: Optional[int] = 10


class PaginatedToDoView(BaseModel):
    data: list[ToDoListItem]
    page: int = Field(gt=0)
    limit: int = Field(gt=0,lte=20)
    total: int = Field(gte=0,lte=20)


@app.get("/todos/", response_model=PaginatedToDoView)
def get_todos(pagination_query: Annotated[PaginationQuery, Query()]):
    offset = pagination_query.limit * (pagination_query.page - 1)
    select_query = "SELECT * FROM todos LIMIT ? OFFSET ?;"
    params = (pagination_query.limit, offset)
    result = utils.execute_query(TODO_SQL_DB, select_query, params, return_value=True)
    todo_list_page = [{"id": todo[0], "title": todo[1], "description": todo[2]} for todo in result]
    paginated_todo_view = {
        "data": todo_list_page,
        "page": pagination_query.page,
        "limit": pagination_query.limit,
        "total": len(todo_list_page)
    }
    return paginated_todo_view
