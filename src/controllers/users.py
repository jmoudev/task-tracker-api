from sqlmodel import select

from ..models.users import User


def get_user(email, session):
    statement = select(User).where(User.email == email)
    user = session.exec(statement).one()
    return user
