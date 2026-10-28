"""Microservicio de Pedidos: registra pedidos y consulta su estado.

Depende de Clientes y Productos, a los que consulta por HTTP (API REST).
"""
import os
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

URL_PRODUCTOS = os.getenv("URL_PRODUCTOS", "http://127.0.0.1:8001")
URL_CLIENTES = os.getenv("URL_CLIENTES", "http://127.0.0.1:8002")
TIEMPO_ESPERA = 2.0   # segundos por intento
REINTENTOS = 2        # intentos adicionales ante fallo de red

app = FastAPI(title="Servicio de Pedidos", version="1.0")
# CORS: permite que la página web de la tienda (aplicación cliente) consuma la API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ItemPedido(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


class PedidoIn(BaseModel):
    cliente_id: int
    items: list[ItemPedido] = Field(min_length=1)


class Pedido(BaseModel):
    id: int
    cliente_id: int
    items: list[ItemPedido]
    total: float
    estado: str
    fecha: str


pedidos: list[Pedido] = []


def consultar_servicio(url: str, nombre_servicio: str) -> httpx.Response:
    """GET con tiempo de espera y reintentos; si el servicio no responde, devuelve 503."""
    ultimo_error = None
    for _ in range(REINTENTOS + 1):
        try:
            return httpx.get(url, timeout=TIEMPO_ESPERA)
        except httpx.RequestError as error:
            ultimo_error = error
    raise HTTPException(
        status_code=503,
        detail=f"Servicio de {nombre_servicio} no disponible ({type(ultimo_error).__name__}). "
               "El pedido no se registró; intente más tarde.",
    )


@app.get("/salud")
def salud():
    return {"servicio": "pedidos", "estado": "activo"}


@app.post("/pedidos", response_model=Pedido, status_code=201)
def registrar_pedido(datos: PedidoIn):
    # 1. Validar el cliente en el servicio de Clientes
    r = consultar_servicio(f"{URL_CLIENTES}/clientes/{datos.cliente_id}", "clientes")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="El cliente no existe")

    # 2. Validar cada producto y calcular el total con el servicio de Productos
    total = 0.0
    for item in datos.items:
        r = consultar_servicio(f"{URL_PRODUCTOS}/productos/{item.producto_id}", "productos")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail=f"El producto {item.producto_id} no existe")
        producto = r.json()
        if producto["stock"] < item.cantidad:
            raise HTTPException(status_code=409, detail=f"Stock insuficiente de {producto['nombre']}")
        total += producto["precio"] * item.cantidad

    pedido = Pedido(
        id=len(pedidos) + 1,
        cliente_id=datos.cliente_id,
        items=datos.items,
        total=total,
        estado="REGISTRADO",
        fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    pedidos.append(pedido)
    return pedido


@app.get("/pedidos/{pedido_id}", response_model=Pedido)
def consultar_estado(pedido_id: int):
    for p in pedidos:
        if p.id == pedido_id:
            return p
    raise HTTPException(status_code=404, detail="Pedido no encontrado")


@app.get("/pedidos", response_model=list[Pedido])
def listar_pedidos():
    return pedidos
