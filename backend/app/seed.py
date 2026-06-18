"""Seed database with demo data."""

from datetime import date
from decimal import Decimal

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import (
    Category,
    POStatus,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
    User,
    UserRole,
)


def seed():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "admin@ims.local").first():
            print("Database already seeded, skipping.")
            return

        admin = User(
            email="admin@ims.local",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.admin,
        )
        staff = User(
            email="staff@ims.local",
            hashed_password=get_password_hash("staff123"),
            full_name="Staff User",
            role=UserRole.staff,
        )
        db.add_all([admin, staff])
        db.flush()

        electronics = Category(name="Electronics", description="Electronic components and devices")
        office = Category(name="Office Supplies", description="General office items")
        db.add_all([electronics, office])
        db.flush()

        products = [
            Product(sku="ELEC-001", name="USB-C Cable", category_id=electronics.id, quantity=50, reorder_level=20, unit_price=Decimal("12.99")),
            Product(sku="ELEC-002", name="Wireless Mouse", category_id=electronics.id, quantity=8, reorder_level=15, unit_price=Decimal("29.99")),
            Product(sku="OFF-001", name="A4 Paper Ream", category_id=office.id, quantity=100, reorder_level=30, unit_price=Decimal("5.49")),
            Product(sku="OFF-002", name="Ballpoint Pens (Box)", category_id=office.id, quantity=5, reorder_level=10, unit_price=Decimal("8.99")),
        ]
        db.add_all(products)
        db.flush()

        suppliers = [
            Supplier(name="TechParts Inc", contact_name="John Smith", email="john@techparts.com", phone="555-0100"),
            Supplier(name="Office Depot Wholesale", contact_name="Jane Doe", email="jane@officedepot.com", phone="555-0200"),
        ]
        db.add_all(suppliers)
        db.flush()

        po = PurchaseOrder(
            po_number="PO-DEMO0001",
            supplier_id=suppliers[0].id,
            created_by=admin.id,
            status=POStatus.draft,
            expected_date=date.today(),
            notes="Demo purchase order",
        )
        db.add(po)
        db.flush()
        db.add(
            PurchaseOrderItem(
                purchase_order_id=po.id,
                product_id=products[1].id,
                quantity_ordered=20,
                unit_cost=Decimal("22.00"),
            )
        )

        db.commit()
        print("Database seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
