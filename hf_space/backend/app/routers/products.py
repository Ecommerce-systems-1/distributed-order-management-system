from fastapi import APIRouter
from app.data.products import PRODUCTS

router = APIRouter(tags=["products"])


@router.get("/products")
def list_products():
    return {"products": PRODUCTS}
