"""Generic CRUD repository base."""
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT], db: Session):
        self.model = model
        self.db = db

    def get(self, id_: UUID) -> Optional[ModelT]:
        return self.db.query(self.model).filter(self.model.id == id_).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelT]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> ModelT:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id_: UUID) -> bool:
        obj = self.get(id_)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True