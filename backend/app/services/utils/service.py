from typing import Any, Type

from sqlalchemy.orm import Session


class BaseService:
    def __init__(self, db: Session):
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: Any) -> Any:
        self.db.refresh(instance)
        return instance

    def commit_and_refresh(self, instance: Any) -> Any:
        self.commit()
        return self.refresh(instance)

    def add(self, instance: Any) -> Any:
        self.db.add(instance)
        return instance

    def add_and_flush(self, instance: Any) -> Any:
        self.add(instance)
        self.db.flush()
        return instance

    def save(self, instance: Any, *, refresh: bool = True) -> Any:
        self.add(instance)
        if refresh:
            return self.commit_and_refresh(instance)
        self.commit()
        return instance

    def create(
        self,
        model_class: Type[Any],
        data: dict[str, Any],
        *,
        commit: bool = True,
        refresh: bool = True,
    ) -> Any:
        instance = model_class(**data)
        self.add(instance)
        if commit:
            if refresh:
                return self.commit_and_refresh(instance)
            self.commit()
        return instance

    def update(
        self,
        instance: Any,
        data: dict[str, Any],
        *,
        commit: bool = True,
        refresh: bool = True,
    ) -> Any:
        for key, value in data.items():
            setattr(instance, key, value)
        if commit:
            if refresh:
                return self.commit_and_refresh(instance)
            self.commit()
        return instance

    def delete(self, instance: Any, *, commit: bool = True) -> Any:
        self.db.delete(instance)
        if commit:
            self.commit()
        return instance

    def get_by_id(self, model_class: Type[Any], instance_id: Any, *, field_name: str = "id") -> Any:
        return self.db.query(model_class).filter(getattr(model_class, field_name) == instance_id).first()

    def get_one(self, model_class: Type[Any], **filters: Any) -> Any:
        query = self.db.query(model_class)
        for key, value in filters.items():
            query = query.filter(getattr(model_class, key) == value)
        return query.first()

    def list_all(self, model_class: Type[Any]) -> list[Any]:
        return self.db.query(model_class).all()
