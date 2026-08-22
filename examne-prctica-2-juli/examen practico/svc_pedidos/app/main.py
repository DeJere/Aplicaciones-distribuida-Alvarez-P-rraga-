import os
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import httpx

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pedidos.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="CREATED")
    total = Column(Float, nullable=False, default=0.0)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="svc-pedidos", version="1.0.0")


class PedidoCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class PedidoItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float


class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    status: str
    total: float
    items: list[PedidoItemResponse]


class OrderService:
    def __init__(self):
        self.catalog_url = os.getenv("CATALOG_URL", "http://svc-catalogo:8000")

    async def _get_catalog_product(self, product_id: int):
        async with httpx.AsyncClient(timeout=2.0) as client:
            return await client.get(f"{self.catalog_url}/api/v1/productos/{product_id}")

    async def create_order(self, payload: PedidoCreate):
        try:
            response = await self._get_catalog_product(payload.product_id)
        except httpx.TimeoutException as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Catalog service timeout") from exc

        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail="Catalog service unavailable")

        product = response.json()
        if product["stock"] < payload.quantity:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Insufficient stock")

        db = SessionLocal()
        try:
            pedido = Pedido(
                product_id=payload.product_id,
                quantity=payload.quantity,
                status="CREATED",
                total=product["precio"] * payload.quantity,
            )
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            return PedidoResponse(
                id=pedido.id,
                product_id=pedido.product_id,
                quantity=pedido.quantity,
                status=pedido.status,
                total=pedido.total,
                items=[
                    PedidoItemResponse(
                        product_id=pedido.product_id,
                        quantity=pedido.quantity,
                        unit_price=product["precio"],
                        subtotal=pedido.total,
                    )
                ],
            )
        finally:
            db.close()


order_service = OrderService()


@app.post("/api/v1/pedidos", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def create_pedido(payload: PedidoCreate, response: Response):
    result = await order_service.create_order(payload)
    response.headers["Location"] = f"/api/v1/pedidos/{result.id}"
    return result


@app.get("/api/v1/pedidos", response_model=list[PedidoResponse])
def list_pedidos():
    db = SessionLocal()
    try:
        pedidos = db.query(Pedido).all()
        return [PedidoResponse.model_validate(pedido) for pedido in pedidos]
    finally:
        db.close()


@app.get("/api/v1/pedidos/{pedido_id}", response_model=PedidoResponse)
def get_pedido(pedido_id: int):
    db = SessionLocal()
    try:
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return PedidoResponse(
            id=pedido.id,
            product_id=pedido.product_id,
            quantity=pedido.quantity,
            status=pedido.status,
            total=pedido.total,
            items=[
                PedidoItemResponse(
                    product_id=pedido.product_id,
                    quantity=pedido.quantity,
                    unit_price=0.0,
                    subtotal=pedido.total,
                )
            ],
        )
    finally:
        db.close()
