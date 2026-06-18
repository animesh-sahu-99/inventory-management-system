from datetime import date, datetime

from sqlalchemy.orm import Session, joinedload

from app.core.pagination import paginate
from app.models.stock_movement import MovementType, StockMovement
from app.repositories.base import BaseRepository


class StockMovementRepository(BaseRepository[StockMovement]):
    def __init__(self, db: Session):
        super().__init__(db, StockMovement)

    def _with_relations(self):
        return (
            self.db.query(StockMovement)
            .options(joinedload(StockMovement.product), joinedload(StockMovement.user))
        )

    def get_by_id_with_relations(self, movement_id: int) -> StockMovement | None:
        return self._with_relations().filter(StockMovement.id == movement_id).first()

    def list_paginated(
        self,
        page: int,
        page_size: int,
        product_id: int | None = None,
        movement_type: MovementType | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[StockMovement], int]:
        query = self._with_relations()
        if product_id:
            query = query.filter(StockMovement.product_id == product_id)
        if movement_type:
            query = query.filter(StockMovement.type == movement_type)
        if start_date:
            query = query.filter(
                StockMovement.created_at >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            query = query.filter(
                StockMovement.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        query = query.order_by(StockMovement.created_at.desc())
        return paginate(query, page, page_size)

    def list_for_report(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[StockMovement]:
        query = self._with_relations().order_by(StockMovement.created_at.desc())
        if start_date:
            query = query.filter(
                StockMovement.created_at >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            query = query.filter(
                StockMovement.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        return query.all()

    def list_recent(self, limit: int = 10) -> list[StockMovement]:
        return self._with_relations().order_by(StockMovement.created_at.desc()).limit(limit).all()
