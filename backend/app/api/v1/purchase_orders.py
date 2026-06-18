from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_po_service, require_admin
from app.models.purchase_order import POStatus
from app.models.user import User
from app.schemas.auth import PaginatedResponse
from app.schemas.purchase_order import POCreate, POOut, POReceive, POUpdate
from app.services.purchase_order_service import PurchaseOrderService

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


@router.get("", response_model=PaginatedResponse[POOut])
def list_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: POStatus | None = None,
    _: User = Depends(get_current_user),
    service: PurchaseOrderService = Depends(get_po_service),
):
    return service.list_paginated(page, page_size, status)


@router.post("", response_model=POOut, status_code=201)
def create_po(
    data: POCreate,
    user: User = Depends(get_current_user),
    service: PurchaseOrderService = Depends(get_po_service),
):
    return PurchaseOrderService.serialize(service.create(user, data))


@router.get("/{po_id}", response_model=POOut)
def get_po(
    po_id: int,
    _: User = Depends(get_current_user),
    service: PurchaseOrderService = Depends(get_po_service),
):
    return PurchaseOrderService.serialize(service.get(po_id))


@router.patch("/{po_id}", response_model=POOut)
def update_po(
    po_id: int,
    data: POUpdate,
    _: User = Depends(get_current_user),
    service: PurchaseOrderService = Depends(get_po_service),
):
    return PurchaseOrderService.serialize(service.update(po_id, data))


@router.post("/{po_id}/submit", response_model=POOut)
def submit_po(
    po_id: int,
    _: User = Depends(get_current_user),
    service: PurchaseOrderService = Depends(get_po_service),
):
    return PurchaseOrderService.serialize(service.submit(po_id))


@router.post("/{po_id}/receive", response_model=POOut)
def receive_po(
    po_id: int,
    data: POReceive,
    user: User = Depends(require_admin),
    service: PurchaseOrderService = Depends(get_po_service),
):
    return PurchaseOrderService.serialize(service.receive(user, po_id, data))


@router.post("/{po_id}/cancel", response_model=POOut)
def cancel_po(
    po_id: int,
    _: User = Depends(require_admin),
    service: PurchaseOrderService = Depends(get_po_service),
):
    return PurchaseOrderService.serialize(service.cancel(po_id))


@router.delete("/{po_id}", status_code=204)
def delete_po(
    po_id: int,
    _: User = Depends(require_admin),
    service: PurchaseOrderService = Depends(get_po_service),
):
    service.delete(po_id)
