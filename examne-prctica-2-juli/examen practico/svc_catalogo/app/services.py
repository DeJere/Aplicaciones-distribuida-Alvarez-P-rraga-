from fastapi import HTTPException, status
from app.repositories import ProductoRepository
from app.schemas import ProductoCreate


class ProductoService:
    def __init__(self, repository: ProductoRepository):
        self.repository = repository

    def create(self, payload: ProductoCreate):
        existing = self.repository.get_by_sku(payload.sku)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")
        return self.repository.create(payload)

    def get_by_id(self, producto_id: int):
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return producto

    def list_all(self):
        return self.repository.list_all()

    def update(self, producto_id: int, payload: ProductoCreate):
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return self.repository.update(producto, payload)

    def delete(self, producto_id: int) -> None:
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        self.repository.delete(producto)
