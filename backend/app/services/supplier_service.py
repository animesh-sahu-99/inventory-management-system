from app.core.exceptions import BadRequestError, NotFoundError
from app.models.supplier import Supplier
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierService:
    def __init__(self, supplier_repo: SupplierRepository):
        self.supplier_repo = supplier_repo

    def list_all(self) -> list[Supplier]:
        return self.supplier_repo.list_all()

    def get(self, supplier_id: int) -> Supplier:
        supplier = self.supplier_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundError("Supplier not found")
        return supplier

    def create(self, data: SupplierCreate) -> Supplier:
        if self.supplier_repo.get_by_name(data.name):
            raise BadRequestError("Supplier already exists")
        supplier = Supplier(**data.model_dump())
        self.supplier_repo.add(supplier)
        self.supplier_repo.commit()
        self.supplier_repo.refresh(supplier)
        return supplier

    def update(self, supplier_id: int, data: SupplierUpdate) -> Supplier:
        supplier = self.get(supplier_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(supplier, key, value)
        self.supplier_repo.commit()
        self.supplier_repo.refresh(supplier)
        return supplier

    def delete(self, supplier_id: int) -> None:
        supplier = self.get(supplier_id)
        if supplier.purchase_orders:
            raise BadRequestError("Cannot delete supplier with purchase orders")
        self.supplier_repo.delete(supplier)
        self.supplier_repo.commit()
