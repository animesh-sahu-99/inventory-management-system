from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.purchase_order import POStatus


class POItemCreate(BaseModel):
    product_id: int
    quantity_ordered: int = Field(gt=0)
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0)


class POItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity_ordered: int
    quantity_received: int
    unit_cost: Decimal
    product_name: str | None = None
    product_sku: str | None = None


class POCreate(BaseModel):
    supplier_id: int
    expected_date: date | None = None
    notes: str | None = None
    items: list[POItemCreate] = Field(min_length=1)


class POUpdate(BaseModel):
    supplier_id: int | None = None
    expected_date: date | None = None
    notes: str | None = None
    items: list[POItemCreate] | None = None


class POReceiveItem(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)


class POReceive(BaseModel):
    items: list[POReceiveItem] = Field(min_length=1)


class SupplierBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class POOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    po_number: str
    supplier_id: int
    created_by: int
    status: POStatus
    expected_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    supplier: SupplierBrief | None = None
    items: list[POItemOut] = []
