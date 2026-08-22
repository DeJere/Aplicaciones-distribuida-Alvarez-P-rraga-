from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    sku: str = Field(min_length=1)
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductoResponse(BaseModel):
    id: int
    sku: str
    nombre: str
    precio: float
    stock: int

    @classmethod
    def from_model(cls, producto):
        return cls(
            id=producto.id,
            sku=producto.sku,
            nombre=producto.nombre,
            precio=producto.precio,
            stock=producto.stock,
        )
