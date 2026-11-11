"""Conexión a PostgreSQL con SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SesionLocal = sessionmaker(bind=engine, expire_on_commit=False)
