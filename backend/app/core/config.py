"""Configuración de la app: se lee de variables de entorno o del archivo .env."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py está en backend/app/core/ -> subir 3 carpetas llega a la raíz del proyecto
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Valores de configuración. Cada atributo se busca como variable de entorno."""

    model_config = SettingsConfigDict(env_file=RAIZ_PROYECTO / ".env", extra="ignore")

    database_url: str

    # Clave para firmar los tokens. Larga y aleatoria; nunca se sube a GitHub.
    jwt_secreto: str = Field(min_length=32)
    minutos_token_acceso: int = 15
    dias_token_refresco: int = 7


settings = Settings()
