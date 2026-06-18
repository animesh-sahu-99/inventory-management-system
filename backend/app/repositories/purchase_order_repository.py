from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.pagination import paginate
from app.models.purchase_order import POStatus, PurchaseOrder, PurchaseOrderItem
from app.repositories.base import BaseRepository


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    def __init__(self, db: Session):
        super().__init__(db, PurchaseOrder)

    def add_item(self, item: PurchaseOrderItem) -> PurchaseOrderItem:
        self.db.add(item)
        return item

    def delete_item(self, item: PurchaseOrderItem) -> None:
        self.db.delete(item)

    def _base_query(self):
        return (
            self.db.query(PurchaseOrder)
            .options(
                joinedload(PurchaseOrder.supplier),
                joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product),
            )
        )

    def get_by_id_with_details(self, po_id: int) -> PurchaseOrder | None:
        return self._base_query().filter(PurchaseOrder.id == po_id).first()

    def get_for_update_with_items(self, po_id: int) -> PurchaseOrder | None:
        return self._base_query().filter(PurchaseOrder.id == po_id).with_for_update().first()

    def list_paginated(
        self,
        page: int,
        page_size: int,
        status: POStatus | None = None,
    ) -> tuple[list[PurchaseOrder], int]:
        query = self._base_query()
        if status:
            query = query.filter(PurchaseOrder.status == status)
        query = query.order_by(PurchaseOrder.created_at.desc())
        return paginate(query, page, page_size)

    def list_for_report(self, status: POStatus | None = None) -> list[PurchaseOrder]:
        query = (
            self.db.query(PurchaseOrder)
            .options(joinedload(PurchaseOrder.supplier), joinedload(PurchaseOrder.items))
            .order_by(PurchaseOrder.created_at.desc())
        )
        if status:
            query = query.filter(PurchaseOrder.status == status)
        return query.all()

    def count_open(self) -> int:
        return (
            self.db.query(func.count(PurchaseOrder.id))
            .filter(PurchaseOrder.status.in_([POStatus.draft, POStatus.ordered, POStatus.partial]))
            .scalar()
            or 0
        )
