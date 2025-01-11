from sqlmodel import Session, SQLModel, create_engine


TODO_SQL_DB = "todos.db"
sqlite_url = f"sqlite:///{TODO_SQL_DB}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
