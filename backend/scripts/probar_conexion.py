"""Comprueba que Python puede conectarse a la base de datos de Docker.

Si funciona, la base de datos está lista para recibir conexiones.
"""

from sqlalchemy import text

from app.core.db import engine

with engine.connect() as conexion:
    version = conexion.execute(text("SELECT version()")).scalar_one()

print("Conectado a la base de datos:", version)
