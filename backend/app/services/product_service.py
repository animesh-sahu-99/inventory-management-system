from app.core.exceptions import BadRequestError, NotFoundError
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.auth import PaginatedResponse
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def list_paginated(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        category_id: int | None = None,
    ) -> PaginatedResponse[ProductOut]:
        items, total = self.product_repo.list_paginated(page, page_size, search, category_id)
        return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)

    def list_low_stock(self) -> list[Product]:
        return self.product_repo.list_low_stock()

    def get(self, product_id: int) -> Product:
        product = self.product_repo.get_by_id_with_category(product_id)
        if not product:
            raise NotFoundError("Product not found")
        return product

    def create(self, data: ProductCreate) -> Product:
        if self.product_repo.get_by_sku(data.sku):
            raise BadRequestError("SKU already exists")
        product = Product(**data.model_dump())
        self.product_repo.add(product)
        self.product_repo.commit()
        return self.get(product.id)

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        self.product_repo.commit()
        return self.get(product_id)

    def delete(self, product_id: int) -> None:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")
        self.product_repo.delete(product)
        self.product_repo.commit()
