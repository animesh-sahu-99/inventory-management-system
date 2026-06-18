from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_supplier_service, require_admin
from app.models.user import User
from app.schemas.supplier import SupplierCreate, SupplierOut, SupplierUpdate
from app.services.supplier_service import SupplierService

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierOut])
def list_suppliers(
    _: User = Depends(get_current_user),
    service: SupplierService = Depends(get_supplier_service),
):
    return service.list_all()


@router.post("", response_model=SupplierOut, status_code=201)
def create_supplier(
    data: SupplierCreate,
    _: User = Depends(require_admin),
    service: SupplierService = Depends(get_supplier_service),
):
    return service.create(data)


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(
    supplier_id: int,
    _: User = Depends(get_current_user),
    service: SupplierService = Depends(get_supplier_service),
):
    return service.get(supplier_id)


@router.patch("/{supplier_id}", response_model=SupplierOut)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    _: User = Depends(require_admin),
    service: SupplierService = Depends(get_supplier_service),
):
    return service.update(supplier_id, data)


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(
    supplier_id: int,
    _: User = Depends(require_admin),
    service: SupplierService = Depends(get_supplier_service),
):
    service.delete(supplier_id)
