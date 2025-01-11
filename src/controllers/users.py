from sqlmodel import select

from ..models.users import UserData


def get_user_data(email, session):
    statement = select(UserData).where(UserData.email == email)
    user_data = session.exec(statement).one()
    return user_data
