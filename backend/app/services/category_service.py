from datetime import datetime, timezone

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def list_all(self) -> list[Category]:
        return self.category_repo.list_all()

    def get(self, category_id: int) -> Category:
        cat = self.category_repo.get_by_id(category_id)
        if not cat:
            raise NotFoundError("Category not found")
        return cat

    def create(self, data: CategoryCreate) -> Category:
        if self.category_repo.get_by_name(data.name):
            raise BadRequestError("Category already exists")
        cat = Category(**data.model_dump())
        self.category_repo.add(cat)
        self.category_repo.commit()
        self.category_repo.refresh(cat)
        return cat

    def update(self, category_id: int, data: CategoryUpdate) -> Category:
        cat = self.get(category_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(cat, key, value)
        self.category_repo.commit()
        self.category_repo.refresh(cat)
        return cat

    def delete(self, category_id: int) -> None:
        cat = self.get(category_id)
        if cat.products:
            raise BadRequestError("Cannot delete category with products")
        self.category_repo.delete(cat)
        self.category_repo.commit()
