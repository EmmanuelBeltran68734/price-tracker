from datetime import timedelta

import jwt
import pytest

from app.core.seguridad import (
    ACCESO,
    REFRESCO,
    TokenInvalidoError,
    crear_token,
    crear_token_acceso,
    crear_token_refresco,
    hashear_contrasena,
    leer_token,
    verificar_contrasena,
)

# --- Contraseñas -------------------------------------------------------------


def test_el_hash_no_contiene_la_contrasena():
    hash_guardado = hashear_contrasena("MiClave-Segura-2026")

    assert "MiClave-Segura-2026" not in hash_guardado
    assert hash_guardado.startswith("$argon2")


def test_verificar_contrasena_correcta_e_incorrecta():
    hash_guardado = hashear_contrasena("MiClave-Segura-2026")

    assert verificar_contrasena("MiClave-Segura-2026", hash_guardado) is True
    assert verificar_contrasena("otra-clave", hash_guardado) is False


def test_la_misma_contrasena_da_hashes_distintos():
    # Cada hash lleva una "sal" aleatoria: dos usuarios con la misma clave no se delatan
    assert hashear_contrasena("1234") != hashear_contrasena("1234")


# --- Tokens JWT --------------------------------------------------------------


def test_token_de_acceso_dice_quien_es_el_usuario():
    token = crear_token_acceso(42)
    assert leer_token(token, ACCESO) == 42


def test_token_de_refresco_no_sirve_como_token_de_acceso():
    token = crear_token_refresco(42)

    assert leer_token(token, REFRESCO) == 42
    with pytest.raises(TokenInvalidoError):
        leer_token(token, ACCESO)


def test_token_vencido_es_rechazado():
    token = crear_token(42, ACCESO, timedelta(minutes=-1))  # venció hace un minuto

    with pytest.raises(TokenInvalidoError):
        leer_token(token, ACCESO)


def test_token_modificado_es_rechazado():
    token = crear_token_acceso(42)
    falsificado = token[:-2] + ("aa" if not token.endswith("aa") else "bb")

    with pytest.raises(TokenInvalidoError):
        leer_token(falsificado, ACCESO)


def test_token_firmado_con_otro_secreto_es_rechazado():
    falso = jwt.encode(
        {"sub": "1", "tipo": ACCESO}, "secreto-de-un-atacante-0123456789", algorithm="HS256"
    )

    with pytest.raises(TokenInvalidoError):
        leer_token(falso, ACCESO)
