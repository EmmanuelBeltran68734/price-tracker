"""Clase base de la que heredan todas las demás tablas."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Nombres predecibles para claves e índices: Alembic los usa para crear y borrar.
CONVENCION_DE_NOMBRES = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Todas las tablas heredan de aquí y quedan registradas en Base.metadata."""

    metadata = MetaData(naming_convention=CONVENCION_DE_NOMBRES)
