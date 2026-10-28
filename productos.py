"""Microservicio de Productos: administra el catálogo de la tienda virtual."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Servicio de Productos", version="1.0")
# CORS: permite que la página web de la tienda (aplicación cliente) consuma la API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ProductoIn(BaseModel):
    nombre: str = Field(min_length=2)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


class Producto(ProductoIn):
    id: int


# Lista en memoria (en un sistema real: base de datos propia del servicio)
productos: list[Producto] = [
    Producto(id=1, nombre="Portátil 14 pulgadas", precio=2_800_000, stock=10),
    Producto(id=2, nombre="Mouse inalámbrico", precio=85_000, stock=50),
]


@app.get("/salud")
def salud():
    return {"servicio": "productos", "estado": "activo"}


@app.get("/productos", response_model=list[Producto])
def listar_productos():
    return productos


@app.get("/productos/{producto_id}", response_model=Producto)
def consultar_producto(producto_id: int):
    for p in productos:
        if p.id == producto_id:
            return p
    raise HTTPException(status_code=404, detail="Producto no encontrado")


@app.post("/productos", response_model=Producto, status_code=201)
def registrar_producto(datos: ProductoIn):
    nuevo = Producto(id=max((p.id for p in productos), default=0) + 1, **datos.model_dump())
    productos.append(nuevo)
    return nuevo
