from fastapi import APIRouter

from app.api.v1 import auth, categories, dashboard, products, purchase_orders, stock_movements, suppliers

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(suppliers.router)
api_router.include_router(purchase_orders.router)
api_router.include_router(stock_movements.router)
api_router.include_router(dashboard.router)
