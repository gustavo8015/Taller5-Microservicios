"""Microservicio de Clientes: registra y consulta los clientes de la tienda."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Servicio de Clientes", version="1.0")
# CORS: permite que la página web de la tienda (aplicación cliente) consuma la API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ClienteIn(BaseModel):
    nombre: str = Field(min_length=2)
    correo: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Cliente(ClienteIn):
    id: int


clientes: list[Cliente] = [
    Cliente(id=1, nombre="Laura Gómez", correo="laura.gomez@correo.com"),
]


@app.get("/salud")
def salud():
    return {"servicio": "clientes", "estado": "activo"}


@app.get("/clientes", response_model=list[Cliente])
def listar_clientes():
    return clientes


@app.get("/clientes/{cliente_id}", response_model=Cliente)
def consultar_cliente(cliente_id: int):
    for c in clientes:
        if c.id == cliente_id:
            return c
    raise HTTPException(status_code=404, detail="Cliente no encontrado")


@app.post("/clientes", response_model=Cliente, status_code=201)
def registrar_cliente(datos: ClienteIn):
    if any(c.correo == datos.correo for c in clientes):
        raise HTTPException(status_code=409, detail="El correo ya está registrado")
    nuevo = Cliente(id=max((c.id for c in clientes), default=0) + 1, **datos.model_dump())
    clientes.append(nuevo)
    return nuevo
