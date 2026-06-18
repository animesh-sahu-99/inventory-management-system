from typing import TypeVar

from sqlalchemy.orm import Query

T = TypeVar("T")


def paginate(query: Query, page: int, page_size: int) -> tuple[list[T], int]:
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total
