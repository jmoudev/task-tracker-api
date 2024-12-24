from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

import utils


TODO_JSON_FILENAME = "todos.json"

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
    todo_data = utils.read_todo_data(TODO_JSON_FILENAME)
    todo_id = todo_data["metadata"]["todo_count"] + 1
    todo_list_item = {"id": todo_id} | todo.dict()
    todo_data["todos"][str(todo_id)] = todo_list_item
    todo_data["metadata"]["todo_count"] += 1
    utils.write_json(TODO_JSON_FILENAME, todo_data)
    return todo_list_item


@app.put("/todos/{todo_id}", response_model=ToDoListItem)
def update_todo(todo_id: int, todo: ToDo):
    todo_data = utils.read_todo_data(TODO_JSON_FILENAME)
    if not todo_data["todos"].get(str(todo_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"todo not found (id {todo_id})")
    todo_list_item = {"id": todo_id} | todo.dict()
    todo_data["todos"][str(todo_id)] = todo_list_item
    utils.write_json(TODO_JSON_FILENAME, todo_data)
    return todo_list_item


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    todo_data = utils.read_todo_data(TODO_JSON_FILENAME)
    try:
        del todo_data["todos"][str(todo_id)]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"todo not found (id {todo_id})")
    utils.write_json(TODO_JSON_FILENAME, todo_data)
