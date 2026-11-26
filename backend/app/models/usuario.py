"""Tabla de usuarios de la API."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Rol(StrEnum):
    """Roles posibles. Un StrEnum se comporta como texto: Rol.ADMIN == "admin"."""

    USUARIO = "usuario"
    ADMIN = "admin"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hash_contrasena: Mapped[str] = mapped_column(String(255))
    rol: Mapped[Rol] = mapped_column(
        Enum(
            Rol,
            name="rol",
            # Se guarda como texto (VARCHAR) y no como un tipo especial de Postgres
            native_enum=False,
            # La base de datos rechaza cualquier rol que no esté en la lista
            create_constraint=True,
            # Guarda el valor ("admin") y no el nombre ("ADMIN")
            values_callable=lambda roles: [rol.value for rol in roles],
        ),
        default=Rol.USUARIO,
    )
    activo: Mapped[bool] = mapped_column(default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
