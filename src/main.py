from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, select

from .authentication import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from .controllers.users import get_user_data
from .database import create_db_and_tables, get_session
from .models.todos import PaginatedToDoView, PaginationQuery, ToDo
from .models.users import Token, TokenData, User, UserData


SessionDep = Annotated[Session, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "Hello, world!"}


@app.post("/register", response_model=Token)
def create_user(user: User, session: SessionDep):
    hashed_password = get_password_hash(user.password)
    user_data = UserData(
        name=user.name, email=user.email, hashed_password=hashed_password
    )
    session.add(user_data)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"email must be unique ('{user.email}')",
        )
    session.refresh(user_data)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {"sub": user_data.email}, expires_delta=access_token_expires
    )
    return Token(token=token)


@app.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    user_data = authenticate_user(session, form_data.username, form_data.password)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {"sub": user_data.email}, expires_delta=access_token_expires
    )
    return Token(token=token)


@app.get("/users")
def get_users(session: SessionDep):
    statement = select(UserData)
    users = session.exec(statement).all()
    return users


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_data(session=session, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: ToDo, user: Annotated[User, Depends(get_current_user)], session: SessionDep
) -> ToDo:
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
def update_todo(
    todo_id: int,
    todo: ToDo,
    session: SessionDep,
    user: Annotated[User, Depends(get_current_user)],
) -> ToDo:
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
def delete_todo(
    todo_id: int, session: SessionDep, user: Annotated[User, Depends(get_current_user)]
) -> None:
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
