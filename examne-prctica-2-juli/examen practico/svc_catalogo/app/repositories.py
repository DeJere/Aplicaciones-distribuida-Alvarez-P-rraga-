from sqlalchemy.orm import Session
from app.models import Producto


class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload) -> Producto:
        producto = Producto(**payload.dict())
        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def get_by_id(self, producto_id: int):
        return self.db.query(Producto).filter(Producto.id == producto_id).first()

    def get_by_sku(self, sku: str):
        return self.db.query(Producto).filter(Producto.sku == sku).first()

    def list_all(self):
        return self.db.query(Producto).all()

    def update(self, producto, payload) -> Producto:
        for field, value in payload.dict().items():
            setattr(producto, field, value)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def delete(self, producto) -> None:
        self.db.delete(producto)
        self.db.commit()
