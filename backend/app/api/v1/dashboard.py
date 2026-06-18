from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user, get_dashboard_service, get_report_service
from app.models.purchase_order import POStatus
from app.models.user import User
from app.schemas.report import (
    DashboardSummary,
    InventoryReportRow,
    LowStockReportRow,
    MovementReportRow,
    POReportRow,
)
from app.services.report_service import DashboardService, ReportService

router = APIRouter(tags=["dashboard", "reports"])


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(
    _: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    return service.get_summary()


@router.get("/reports/inventory", response_model=list[InventoryReportRow])
def inventory_report(
    _: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    return service.inventory_report()


@router.get("/reports/inventory/export")
def inventory_export(
    _: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    rows = service.inventory_report()
    csv_data = ReportService.to_csv(
        ["SKU", "Name", "Category", "Quantity", "Reorder Level", "Unit Price", "Total Value", "Status"],
        [[r.sku, r.name, r.category, r.quantity, r.reorder_level, r.unit_price, r.total_value, r.status] for r in rows],
    )
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_report.csv"},
    )


@router.get("/reports/low-stock", response_model=list[LowStockReportRow])
def low_stock_report(
    _: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    return service.low_stock_report()


@router.get("/reports/low-stock/export")
def low_stock_export(
    _: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    rows = service.low_stock_report()
    csv_data = ReportService.to_csv(
        ["SKU", "Name", "Category", "Quantity", "Reorder Level", "Deficit"],
        [[r.sku, r.name, r.category, r.quantity, r.reorder_level, r.deficit] for r in rows],
    )
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=low_stock_report.csv"},
    )


@router.get("/reports/movements", response_model=list[MovementReportRow])
def movements_report(
    start_date: str | None = None,
    end_date: str | None = None,
    _: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    from datetime import date as date_type
    sd = date_type.fromisoformat(start_date) if start_date else None
    ed = date_type.fromisoformat(end_date) if end_date else None
    return service.movements_report(sd, ed)


@router.get("/reports/movements/export")
def movements_export(
    start_date: str | None = None,
    end_date: str | None = None,
    _: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    from datetime import date as date_type
    sd = date_type.fromisoformat(start_date) if start_date else None
    ed = date_type.fromisoformat(end_date) if end_date else None
    rows = service.movements_report(sd, ed)
    csv_data = ReportService.to_csv(
        ["ID", "Date", "SKU", "Product", "Type", "Quantity", "User", "Note"],
        [[r.id, r.date.isoformat(), r.product_sku, r.product_name, r.type.value, r.quantity, r.user, r.note or ""] for r in rows],
    )
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=movements_report.csv"},
    )


@router.get("/reports/purchase-orders", response_model=list[POReportRow])
def po_report(
    status: POStatus | None = None,
    _: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    return service.purchase_orders_report(status)


@router.get("/reports/purchase-orders/export")
def po_export(
    status: POStatus | None = None,
    _: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    rows = service.purchase_orders_report(status)
    csv_data = ReportService.to_csv(
        ["PO Number", "Supplier", "Status", "Items", "Ordered", "Received", "Created"],
        [[r.po_number, r.supplier, r.status.value, r.total_items, r.total_ordered, r.total_received, r.created_at.isoformat()] for r in rows],
    )
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=purchase_orders_report.csv"},
    )
