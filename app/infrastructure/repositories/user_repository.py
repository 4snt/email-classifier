import bcrypt
from typing import Optional
from sqlmodel import Session, select

from app.domain.entities import User
from app.infrastructure.models import UserModel


class UserRepository:
    """Repositório de usuários baseado em SQLModel."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User, password: str) -> User:
        """Cria um novo usuário com senha criptografada."""
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        model = UserModel.from_entity(user)
        model.password_hash = hashed.decode("utf-8")

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def get_by_username(self, username: str) -> Optional[User]:
        """Busca usuário pelo username."""
        stmt = select(UserModel).where(UserModel.username == username)
        db_obj = self.session.exec(stmt).first()
        return db_obj.to_entity() if db_obj else None

    def verify_password(self, plain: str, hashed: str) -> bool:
        """Valida senha usando bcrypt."""
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
