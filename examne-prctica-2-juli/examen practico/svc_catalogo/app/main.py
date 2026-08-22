import os
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./catalogo.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="svc-catalogo", version="1.0.0")


class ProductoCreate(BaseModel):
    sku: str = Field(min_length=1)
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    nombre: str
    precio: float
    stock: int


@app.post("/api/v1/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def create_producto(payload: ProductoCreate, response: Response):
    db = SessionLocal()
    try:
        existing = db.query(Producto).filter(Producto.sku == payload.sku).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")
        producto = Producto(**payload.model_dump())
        db.add(producto)
        db.commit()
        db.refresh(producto)
        response.headers["Location"] = f"/api/v1/productos/{producto.id}"
        return ProductoResponse.model_validate(producto)
    finally:
        db.close()


@app.get("/api/v1/productos/{producto_id}", response_model=ProductoResponse)
def get_producto(producto_id: int):
    db = SessionLocal()
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return ProductoResponse.model_validate(producto)
    finally:
        db.close()


@app.get("/api/v1/productos", response_model=list[ProductoResponse])
def list_productos():
    db = SessionLocal()
    try:
        return [ProductoResponse.model_validate(producto) for producto in db.query(Producto).all()]
    finally:
        db.close()


@app.put("/api/v1/productos/{producto_id}", response_model=ProductoResponse)
def update_producto(producto_id: int, payload: ProductoCreate):
    db = SessionLocal()
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        for field, value in payload.model_dump().items():
            setattr(producto, field, value)
        db.commit()
        db.refresh(producto)
        return ProductoResponse.model_validate(producto)
    finally:
        db.close()


@app.delete("/api/v1/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(producto_id: int):
    db = SessionLocal()
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        db.delete(producto)
        db.commit()
    finally:
        db.close()
