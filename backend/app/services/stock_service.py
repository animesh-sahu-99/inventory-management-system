from datetime import datetime, timezone

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.product import Product
from app.models.stock_movement import MovementType, StockMovement
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.repositories.stock_movement_repository import StockMovementRepository
from app.schemas.auth import PaginatedResponse
from app.schemas.stock_movement import StockMovementOut


class StockService:
    def __init__(
        self,
        product_repo: ProductRepository,
        movement_repo: StockMovementRepository,
    ):
        self.product_repo = product_repo
        self.movement_repo = movement_repo

    def apply_movement(
        self,
        product: Product,
        user: User,
        movement_type: MovementType,
        quantity: int,
        note: str | None = None,
        purchase_order_id: int | None = None,
        commit: bool = True,
    ) -> StockMovement:
        if movement_type == MovementType.IN:
            product.quantity += quantity
        elif movement_type == MovementType.OUT:
            if product.quantity < quantity:
                raise BadRequestError(
                    f"Insufficient stock. Available: {product.quantity}, requested: {quantity}"
                )
            product.quantity -= quantity
        elif movement_type == MovementType.ADJUSTMENT:
            product.quantity = quantity

        product.updated_at = datetime.now(timezone.utc)

        movement = StockMovement(
            product_id=product.id,
            user_id=user.id,
            purchase_order_id=purchase_order_id,
            type=movement_type,
            quantity=quantity,
            note=note,
        )
        self.movement_repo.add(movement)
        if commit:
            self.movement_repo.commit()
            self.movement_repo.refresh(movement)
        return movement

    def create_manual_movement(
        self,
        user: User,
        product_id: int,
        movement_type: MovementType,
        quantity: int,
        note: str | None = None,
    ) -> StockMovement:
        product = self.product_repo.get_for_update(product_id)
        if not product:
            raise NotFoundError("Product not found")
        return self.apply_movement(product, user, movement_type, quantity, note)

    def list_paginated(
        self,
        page: int,
        page_size: int,
        product_id: int | None = None,
        movement_type: MovementType | None = None,
        start_date=None,
        end_date=None,
    ) -> PaginatedResponse[StockMovementOut]:
        items, total = self.movement_repo.list_paginated(
            page, page_size, product_id, movement_type, start_date, end_date
        )
        return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)

    def get_with_relations(self, movement_id: int) -> StockMovement:
        movement = self.movement_repo.get_by_id_with_relations(movement_id)
        if not movement:
            raise NotFoundError("Stock movement not found")
        return movement
