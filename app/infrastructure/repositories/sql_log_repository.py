from typing import List, Optional
from sqlmodel import Session, select

from app.domain.entities import ClassificationLog
from app.domain.ports import LogRepositoryPort
from app.infrastructure.models import ClassificationLogModel


class SqlLogRepository(LogRepositoryPort):
    """Implementação de LogRepositoryPort com SQLModel."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, log: ClassificationLog) -> ClassificationLog:
        db_obj = ClassificationLogModel.from_entity(log)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj.to_entity()

    def list_recent(self, limit: int = 50) -> List[ClassificationLog]:
        stmt = select(ClassificationLogModel).order_by(
            ClassificationLogModel.created_at.desc()
        ).limit(limit)
        results = self.session.exec(stmt).all()
        return [obj.to_entity() for obj in results]

    def get_by_id(self, log_id: int) -> Optional[ClassificationLog]:
        db_obj = self.session.get(ClassificationLogModel, log_id)
        return db_obj.to_entity() if db_obj else None
