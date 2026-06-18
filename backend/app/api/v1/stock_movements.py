from datetime import date

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_stock_service
from app.models.stock_movement import MovementType
from app.models.user import User
from app.schemas.auth import PaginatedResponse
from app.schemas.stock_movement import StockMovementCreate, StockMovementOut
from app.services.stock_service import StockService

router = APIRouter(prefix="/stock-movements", tags=["stock-movements"])


@router.get("", response_model=PaginatedResponse[StockMovementOut])
def list_movements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_id: int | None = None,
    movement_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    _: User = Depends(get_current_user),
    service: StockService = Depends(get_stock_service),
):
    mtype = MovementType(movement_type) if movement_type else None
    return service.list_paginated(page, page_size, product_id, mtype, start_date, end_date)


@router.post("", response_model=StockMovementOut, status_code=201)
def create_movement(
    data: StockMovementCreate,
    user: User = Depends(get_current_user),
    service: StockService = Depends(get_stock_service),
):
    movement = service.create_manual_movement(
        user, data.product_id, data.type, data.quantity, data.note
    )
    return service.get_with_relations(movement.id)
