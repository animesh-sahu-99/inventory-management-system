from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.stock_movement import MovementType


class StockMovementCreate(BaseModel):
    product_id: int
    type: MovementType
    quantity: int = Field(gt=0)
    note: str | None = None


class ProductBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str


class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str


class StockMovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    user_id: int
    purchase_order_id: int | None
    type: MovementType
    quantity: int
    note: str | None
    created_at: datetime
    product: ProductBrief | None = None
    user: UserBrief | None = None
