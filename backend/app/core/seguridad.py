"""Seguridad: hash de contraseñas y tokens JWT."""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITMO = "HS256"
ACCESO = "acceso"
REFRESCO = "refresco"

# Argon2: el algoritmo recomendado hoy para guardar contraseñas
hasher = PasswordHash.recommended()


class TokenInvalidoError(Exception):
    """El token está vencido, fue modificado o no es del tipo esperado."""


def hashear_contrasena(contrasena: str) -> str:
    """Devuelve el hash de la contraseña. Es lo único que se guarda en la base de datos."""
    return hasher.hash(contrasena)


def verificar_contrasena(contrasena: str, hash_guardado: str) -> bool:
    """Comprueba si la contraseña escrita corresponde al hash guardado."""
    return hasher.verify(contrasena, hash_guardado)


def crear_token(usuario_id: int, tipo: str, duracion: timedelta) -> str:
    """Crea un JWT firmado que dice quién es el usuario y hasta cuándo vale."""
    ahora = datetime.now(UTC)
    datos = {"sub": str(usuario_id), "tipo": tipo, "iat": ahora, "exp": ahora + duracion}
    return jwt.encode(datos, settings.jwt_secreto, algorithm=ALGORITMO)


def crear_token_acceso(usuario_id: int) -> str:
    """Token corto (15 min) que se envía en cada petición."""
    return crear_token(usuario_id, ACCESO, timedelta(minutes=settings.minutos_token_acceso))


def crear_token_refresco(usuario_id: int) -> str:
    """Token largo (7 días) que solo sirve para pedir un token de acceso nuevo."""
    return crear_token(usuario_id, REFRESCO, timedelta(days=settings.dias_token_refresco))


def leer_token(token: str, tipo_esperado: str) -> int:
    """Verifica la firma, la fecha y el tipo del token. Devuelve el id del usuario."""
    try:
        datos = jwt.decode(token, settings.jwt_secreto, algorithms=[ALGORITMO])
    except jwt.InvalidTokenError as error:
        raise TokenInvalidoError("Token inválido o vencido") from error

    if datos.get("tipo") != tipo_esperado:
        raise TokenInvalidoError(f"Se esperaba un token de {tipo_esperado}")
    return int(datos["sub"])
