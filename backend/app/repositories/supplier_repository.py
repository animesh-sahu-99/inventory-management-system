from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: Session):
        super().__init__(db, Supplier)

    def get_by_name(self, name: str) -> Supplier | None:
        return self.db.query(Supplier).filter(Supplier.name == name).first()

    def list_all(self) -> list[Supplier]:
        return self.db.query(Supplier).order_by(Supplier.name).all()

    def count(self) -> int:
        return self.db.query(func.count(Supplier.id)).scalar() or 0
