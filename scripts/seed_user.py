from sqlmodel import Session
from app.infrastructure.db import engine
from app.domain.entities import User
from app.infrastructure.repositories.user_repository import UserRepository


def seed():
    with Session(engine) as session:
        repo = UserRepository(session)
        if repo.get_by_username("murilo"):
            print("⚠️ Usuário 'murilo' já existe")
            return

        user_entity = User(id=None, username="murilo", password_hash="")
        user = repo.create(user_entity, "1234")

        print(f"✅ Usuário criado: {user.username} (id={user.id})")


if __name__ == "__main__":
    seed()
