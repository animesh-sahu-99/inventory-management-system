from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(db, Category)

    def get_by_name(self, name: str) -> Category | None:
        return self.db.query(Category).filter(Category.name == name).first()

    def list_all(self) -> list[Category]:
        return self.db.query(Category).order_by(Category.name).all()

    def count(self) -> int:
        return self.db.query(Category).count()
