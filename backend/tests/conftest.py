"""Configuración común de pytest: se ejecuta antes que cualquier test."""

import os

# Valores SOLO para los tests. En el CI de GitHub no existe .env, así que los ponemos aquí.
# setdefault no pisa los valores si ya existen en la terminal.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRETO", "secreto-solo-para-tests-0123456789abcdef")
