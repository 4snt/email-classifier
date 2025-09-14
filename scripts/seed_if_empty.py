from sqlmodel import Session, select
from app.infrastructure.db import engine, init_db
from app.infrastructure.models import UserModel
from app.domain.entities import User
from app.infrastructure.repositories.user_repository import UserRepository


def seed_if_empty():
    print("🔎 Verificando se já existem usuários...")
    init_db()  

    with Session(engine) as session:
        count = session.exec(select(UserModel)).first()
        if count:
            print("✅ Usuários já existem, nada a fazer.")
            return

        print("⚠️ Nenhum usuário encontrado. Criando admin padrão...")
        repo = UserRepository(session)
        user_entity = User(id=None, username="admin", password_hash="")
        user = repo.create(user_entity, "admin123")
        print(f"✅ Usuário criado: {user.username} (id={user.id})")


if __name__ == "__main__":
    seed_if_empty()
