import uuid
from datetime import datetime, timezone

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.purchase_order import POStatus, PurchaseOrder, PurchaseOrderItem
from app.models.user import User
from app.models.stock_movement import MovementType
from app.repositories.product_repository import ProductRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.schemas.auth import PaginatedResponse
from app.schemas.purchase_order import POCreate, POItemOut, POOut, POReceive, POUpdate
from app.services.stock_service import StockService


def _generate_po_number() -> str:
    return f"PO-{uuid.uuid4().hex[:8].upper()}"


class PurchaseOrderService:
    def __init__(
        self,
        po_repo: PurchaseOrderRepository,
        product_repo: ProductRepository,
        stock_service: StockService,
    ):
        self.po_repo = po_repo
        self.product_repo = product_repo
        self.stock_service = stock_service

    def _get_or_raise(self, po_id: int) -> PurchaseOrder:
        po = self.po_repo.get_by_id_with_details(po_id)
        if not po:
            raise NotFoundError("Purchase order not found")
        return po

    def list_paginated(
        self,
        page: int,
        page_size: int,
        status: POStatus | None = None,
    ) -> PaginatedResponse[POOut]:
        orders, total = self.po_repo.list_paginated(page, page_size, status)
        return PaginatedResponse(
            items=[self.serialize(po) for po in orders],
            total=total,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def serialize(po: PurchaseOrder) -> POOut:
        items = []
        for item in po.items:
            out = POItemOut.model_validate(item)
            if item.product:
                out.product_name = item.product.name
                out.product_sku = item.product.sku
            items.append(out)
        po_out = POOut.model_validate(po)
        po_out.items = items
        return po_out

    def create(self, user: User, data: POCreate) -> PurchaseOrder:
        po = PurchaseOrder(
            po_number=_generate_po_number(),
            supplier_id=data.supplier_id,
            created_by=user.id,
            expected_date=data.expected_date,
            notes=data.notes,
            status=POStatus.draft,
        )
        self.po_repo.add(po)
        self.po_repo.flush()

        for item in data.items:
            product = self.product_repo.get_by_id(item.product_id)
            if not product:
                raise NotFoundError(f"Product {item.product_id} not found")
            self.po_repo.add_item(
                PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=item.product_id,
                    quantity_ordered=item.quantity_ordered,
                    unit_cost=item.unit_cost,
                )
            )
        self.po_repo.commit()
        return self._get_or_raise(po.id)

    def get(self, po_id: int) -> PurchaseOrder:
        return self._get_or_raise(po_id)

    def update(self, po_id: int, data: POUpdate) -> PurchaseOrder:
        po = self._get_or_raise(po_id)
        if po.status != POStatus.draft:
            raise BadRequestError("Only draft POs can be edited")

        if data.supplier_id is not None:
            po.supplier_id = data.supplier_id
        if data.expected_date is not None:
            po.expected_date = data.expected_date
        if data.notes is not None:
            po.notes = data.notes
        if data.items is not None:
            for item in po.items:
                self.po_repo.delete_item(item)
            self.po_repo.flush()
            for item in data.items:
                self.po_repo.add_item(
                    PurchaseOrderItem(
                        purchase_order_id=po.id,
                        product_id=item.product_id,
                        quantity_ordered=item.quantity_ordered,
                        unit_cost=item.unit_cost,
                    )
                )

        po.updated_at = datetime.now(timezone.utc)
        self.po_repo.commit()
        return self._get_or_raise(po_id)

    def submit(self, po_id: int) -> PurchaseOrder:
        po = self._get_or_raise(po_id)
        if po.status != POStatus.draft:
            raise BadRequestError("Only draft POs can be submitted")
        if not po.items:
            raise BadRequestError("PO must have at least one item")
        po.status = POStatus.ordered
        po.updated_at = datetime.now(timezone.utc)
        self.po_repo.commit()
        return self._get_or_raise(po_id)

    def receive(self, user: User, po_id: int, data: POReceive) -> PurchaseOrder:
        po = self.po_repo.get_for_update_with_items(po_id)
        if not po:
            raise NotFoundError("Purchase order not found")
        if po.status not in (POStatus.ordered, POStatus.partial):
            raise BadRequestError("PO must be ordered or partial to receive")

        item_map = {item.id: item for item in po.items}
        for recv in data.items:
            item = item_map.get(recv.item_id)
            if not item:
                raise NotFoundError(f"PO item {recv.item_id} not found")
            remaining = item.quantity_ordered - item.quantity_received
            if recv.quantity > remaining:
                raise BadRequestError(
                    f"Cannot receive {recv.quantity} for item {recv.item_id}. Remaining: {remaining}"
                )
            product = self.product_repo.get_for_update(item.product_id)
            self.stock_service.apply_movement(
                product,
                user,
                MovementType.IN,
                recv.quantity,
                note=f"Received from PO {po.po_number}",
                purchase_order_id=po.id,
                commit=False,
            )
            item.quantity_received += recv.quantity

        all_received = all(i.quantity_received >= i.quantity_ordered for i in po.items)
        any_received = any(i.quantity_received > 0 for i in po.items)
        if all_received:
            po.status = POStatus.received
        elif any_received:
            po.status = POStatus.partial

        po.updated_at = datetime.now(timezone.utc)
        self.po_repo.commit()
        return self._get_or_raise(po_id)

    def cancel(self, po_id: int) -> PurchaseOrder:
        po = self._get_or_raise(po_id)
        if po.status in (POStatus.received, POStatus.cancelled):
            raise BadRequestError("Cannot cancel this PO")
        po.status = POStatus.cancelled
        po.updated_at = datetime.now(timezone.utc)
        self.po_repo.commit()
        return self._get_or_raise(po_id)

    def delete(self, po_id: int) -> None:
        po = self._get_or_raise(po_id)
        if po.status != POStatus.draft:
            raise BadRequestError("Only draft POs can be deleted")
        self.po_repo.delete(po)
        self.po_repo.commit()
