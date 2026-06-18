import csv
import io
from datetime import date
from decimal import Decimal

from app.models.purchase_order import POStatus
from app.repositories.product_repository import ProductRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.stock_movement_repository import StockMovementRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.report import (
    DashboardSummary,
    InventoryReportRow,
    LowStockReportRow,
    MovementReportRow,
    POReportRow,
)


def _stock_status(quantity: int, reorder_level: int) -> str:
    if quantity == 0:
        return "Out"
    if quantity <= reorder_level:
        return "Low"
    return "OK"


class DashboardService:
    def __init__(
        self,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
        supplier_repo: SupplierRepository,
        po_repo: PurchaseOrderRepository,
        movement_repo: StockMovementRepository,
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.supplier_repo = supplier_repo
        self.po_repo = po_repo
        self.movement_repo = movement_repo

    def get_summary(self) -> DashboardSummary:
        products = self.product_repo.list_with_category()
        total_value = sum(Decimal(str(p.unit_price)) * p.quantity for p in products)
        return DashboardSummary(
            total_products=self.product_repo.count(),
            total_categories=self.category_repo.count(),
            total_suppliers=self.supplier_repo.count(),
            low_stock_count=self.product_repo.count_low_stock(),
            open_po_count=self.po_repo.count_open(),
            total_inventory_value=total_value,
            recent_movements=self.movement_repo.list_recent(10),
        )


class ReportService:
    def __init__(
        self,
        product_repo: ProductRepository,
        po_repo: PurchaseOrderRepository,
        movement_repo: StockMovementRepository,
    ):
        self.product_repo = product_repo
        self.po_repo = po_repo
        self.movement_repo = movement_repo

    def inventory_report(self) -> list[InventoryReportRow]:
        products = self.product_repo.list_with_category()
        rows = []
        for p in products:
            total_value = Decimal(str(p.unit_price)) * p.quantity
            rows.append(
                InventoryReportRow(
                    sku=p.sku,
                    name=p.name,
                    category=p.category.name if p.category else "",
                    quantity=p.quantity,
                    reorder_level=p.reorder_level,
                    unit_price=p.unit_price,
                    total_value=total_value,
                    status=_stock_status(p.quantity, p.reorder_level),
                )
            )
        return rows

    def low_stock_report(self) -> list[LowStockReportRow]:
        products = self.product_repo.list_low_stock()
        return [
            LowStockReportRow(
                sku=p.sku,
                name=p.name,
                category=p.category.name if p.category else "",
                quantity=p.quantity,
                reorder_level=p.reorder_level,
                deficit=max(0, p.reorder_level - p.quantity),
            )
            for p in products
        ]

    def movements_report(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[MovementReportRow]:
        movements = self.movement_repo.list_for_report(start_date, end_date)
        return [
            MovementReportRow(
                id=m.id,
                date=m.created_at,
                product_sku=m.product.sku if m.product else "",
                product_name=m.product.name if m.product else "",
                type=m.type,
                quantity=m.quantity,
                user=m.user.full_name if m.user else "",
                note=m.note,
            )
            for m in movements
        ]

    def purchase_orders_report(self, status: POStatus | None = None) -> list[POReportRow]:
        orders = self.po_repo.list_for_report(status)
        rows = []
        for po in orders:
            rows.append(
                POReportRow(
                    po_number=po.po_number,
                    supplier=po.supplier.name if po.supplier else "",
                    status=po.status,
                    total_items=len(po.items),
                    total_ordered=sum(i.quantity_ordered for i in po.items),
                    total_received=sum(i.quantity_received for i in po.items),
                    created_at=po.created_at,
                )
            )
        return rows

    @staticmethod
    def to_csv(headers: list[str], rows: list[list]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
