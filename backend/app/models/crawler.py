"""Tablas del crawler: tiendas, productos, historial de precios y ejecuciones."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tienda(Base):
    __tablename__ = "tiendas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    dominio: Mapped[str] = mapped_column(String(255), unique=True)

    productos: Mapped[list["Producto"]] = relationship(back_populates="tienda")


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tienda_id: Mapped[int] = mapped_column(ForeignKey("tiendas.id"), index=True)
    url: Mapped[str] = mapped_column(Text, unique=True)
    nombre: Mapped[str | None] = mapped_column(String(500))
    imagen_url: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tienda: Mapped[Tienda] = relationship(back_populates="productos")
    precios: Mapped[list["HistorialPrecio"]] = relationship(back_populates="producto")


class HistorialPrecio(Base):
    __tablename__ = "historial_precios"
    __table_args__ = (CheckConstraint("precio > 0", name="precio_positivo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id", ondelete="CASCADE"), index=True
    )
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    moneda: Mapped[str] = mapped_column(String(3), default="COP")
    disponible: Mapped[bool]
    capturado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    producto: Mapped[Producto] = relationship(back_populates="precios")


class EjecucionCrawler(Base):
    __tablename__ = "ejecuciones_crawler"

    id: Mapped[int] = mapped_column(primary_key=True)
    iniciado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    terminado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    productos_ok: Mapped[int] = mapped_column(default=0)
    productos_con_error: Mapped[int] = mapped_column(default=0)
    errores: Mapped[str | None] = mapped_column(Text)
