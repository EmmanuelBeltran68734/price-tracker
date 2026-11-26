"""Punto de entrada de la API."""

from fastapi import FastAPI

app = FastAPI(
    title="Price Tracker API",
    description="Vigila precios de tiendas colombianas y avisa cuando bajan.",
    version="0.1.0",
)


@app.get("/salud", tags=["sistema"])
def salud() -> dict[str, str]:
    """Responde si la API está viva. Render lo usará para saber que el servicio funciona."""
    return {"estado": "ok"}
