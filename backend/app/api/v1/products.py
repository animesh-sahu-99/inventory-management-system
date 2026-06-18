from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_product_service
from app.models.user import User
from app.schemas.auth import PaginatedResponse
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=PaginatedResponse[ProductOut])
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category_id: int | None = None,
    _: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    return service.list_paginated(page, page_size, search, category_id)


@router.get("/low-stock", response_model=list[ProductOut])
def low_stock(
    _: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    return service.list_low_stock()


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    data: ProductCreate,
    _: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    return service.create(data)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    _: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    return service.get(product_id)


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    _: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    return service.update(product_id, data)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    _: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    service.delete(product_id)
