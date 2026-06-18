from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.stock_movement_repository import StockMovementRepository
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.services.purchase_order_service import PurchaseOrderService
from app.services.report_service import DashboardService, ReportService
from app.services.stock_service import StockService
from app.services.supplier_service import SupplierService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Repositories ---

def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_category_repo(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)


def get_product_repo(db: Session = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)


def get_supplier_repo(db: Session = Depends(get_db)) -> SupplierRepository:
    return SupplierRepository(db)


def get_po_repo(db: Session = Depends(get_db)) -> PurchaseOrderRepository:
    return PurchaseOrderRepository(db)


def get_movement_repo(db: Session = Depends(get_db)) -> StockMovementRepository:
    return StockMovementRepository(db)


# --- Services ---

def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)


def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repo),
) -> CategoryService:
    return CategoryService(category_repo)


def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repo),
) -> ProductService:
    return ProductService(product_repo)


def get_supplier_service(
    supplier_repo: SupplierRepository = Depends(get_supplier_repo),
) -> SupplierService:
    return SupplierService(supplier_repo)


def get_stock_service(
    product_repo: ProductRepository = Depends(get_product_repo),
    movement_repo: StockMovementRepository = Depends(get_movement_repo),
) -> StockService:
    return StockService(product_repo, movement_repo)


def get_po_service(
    po_repo: PurchaseOrderRepository = Depends(get_po_repo),
    product_repo: ProductRepository = Depends(get_product_repo),
    stock_service: StockService = Depends(get_stock_service),
) -> PurchaseOrderService:
    return PurchaseOrderService(po_repo, product_repo, stock_service)


def get_dashboard_service(
    product_repo: ProductRepository = Depends(get_product_repo),
    category_repo: CategoryRepository = Depends(get_category_repo),
    supplier_repo: SupplierRepository = Depends(get_supplier_repo),
    po_repo: PurchaseOrderRepository = Depends(get_po_repo),
    movement_repo: StockMovementRepository = Depends(get_movement_repo),
) -> DashboardService:
    return DashboardService(product_repo, category_repo, supplier_repo, po_repo, movement_repo)


def get_report_service(
    product_repo: ProductRepository = Depends(get_product_repo),
    po_repo: PurchaseOrderRepository = Depends(get_po_repo),
    movement_repo: StockMovementRepository = Depends(get_movement_repo),
) -> ReportService:
    return ReportService(product_repo, po_repo, movement_repo)


# --- Auth dependencies ---

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = UserRepository(db).get_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
