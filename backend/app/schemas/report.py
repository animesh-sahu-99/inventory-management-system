from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.purchase_order import POStatus
from app.models.stock_movement import MovementType
from app.schemas.stock_movement import StockMovementOut


class DashboardSummary(BaseModel):
    total_products: int
    total_categories: int
    total_suppliers: int
    low_stock_count: int
    open_po_count: int
    total_inventory_value: Decimal
    recent_movements: list[StockMovementOut]


class InventoryReportRow(BaseModel):
    sku: str
    name: str
    category: str
    quantity: int
    reorder_level: int
    unit_price: Decimal
    total_value: Decimal
    status: str


class LowStockReportRow(BaseModel):
    sku: str
    name: str
    category: str
    quantity: int
    reorder_level: int
    deficit: int


class MovementReportRow(BaseModel):
    id: int
    date: datetime
    product_sku: str
    product_name: str
    type: MovementType
    quantity: int
    user: str
    note: str | None


class POReportRow(BaseModel):
    po_number: str
    supplier: str
    status: POStatus
    total_items: int
    total_ordered: int
    total_received: int
    created_at: datetime
