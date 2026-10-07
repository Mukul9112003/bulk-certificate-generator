from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from models.user import User
from repositories.base import UserRepository


class SQLAlchemyUserRepository(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def get_all(self) -> list[User]:
        statement = select(User)

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)

        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()