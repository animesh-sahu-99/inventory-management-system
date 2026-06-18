from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.pagination import paginate
from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(db, Product)

    def _with_category(self):
        return self.db.query(Product).options(joinedload(Product.category))

    def get_by_id_with_category(self, product_id: int) -> Product | None:
        return self._with_category().filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str) -> Product | None:
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_for_update(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).with_for_update().first()

    def list_paginated(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        category_id: int | None = None,
    ) -> tuple[list[Product], int]:
        query = self._with_category()
        if search:
            query = query.filter(
                (Product.name.ilike(f"%{search}%")) | (Product.sku.ilike(f"%{search}%"))
            )
        if category_id:
            query = query.filter(Product.category_id == category_id)
        query = query.order_by(Product.name)
        return paginate(query, page, page_size)

    def list_low_stock(self) -> list[Product]:
        return (
            self._with_category()
            .filter(Product.quantity <= Product.reorder_level)
            .order_by(Product.quantity)
            .all()
        )

    def list_with_category(self) -> list[Product]:
        return self._with_category().all()

    def count(self) -> int:
        return self.db.query(func.count(Product.id)).scalar() or 0

    def count_low_stock(self) -> int:
        return (
            self.db.query(func.count(Product.id))
            .filter(Product.quantity <= Product.reorder_level)
            .scalar()
            or 0
        )
