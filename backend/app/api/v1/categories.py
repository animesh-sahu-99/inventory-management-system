from fastapi import APIRouter, Depends

from app.core.deps import get_category_service, get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(
    _: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return service.list_all()


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    data: CategoryCreate,
    _: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return service.create(data)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    _: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return service.get(category_id)


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    _: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return service.update(category_id, data)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    _: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    service.delete(category_id)
