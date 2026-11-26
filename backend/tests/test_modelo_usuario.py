import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Base, Rol, Usuario


@pytest.fixture
def sesion():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_usuario_nuevo_tiene_rol_usuario_y_esta_activo(sesion):
    usuario = Usuario(email="emma@example.com", hash_contrasena="hash-falso")
    sesion.add(usuario)
    sesion.commit()

    assert usuario.rol == Rol.USUARIO
    assert usuario.activo is True


def test_el_rol_se_guarda_como_texto(sesion):
    sesion.add(Usuario(email="admin@example.com", hash_contrasena="x", rol=Rol.ADMIN))
    sesion.commit()

    assert sesion.scalar(text("SELECT rol FROM usuarios")) == "admin"


def test_no_se_repite_el_email(sesion):
    sesion.add(Usuario(email="emma@example.com", hash_contrasena="x"))
    sesion.commit()
    sesion.add(Usuario(email="emma@example.com", hash_contrasena="y"))

    with pytest.raises(IntegrityError):
        sesion.commit()


def test_la_base_de_datos_rechaza_roles_inventados(sesion):
    sql = text(
        "INSERT INTO usuarios (email, hash_contrasena, rol, activo) "
        "VALUES ('test@example.com', 'x', 'jefe', true)"
    )
    with pytest.raises(IntegrityError):
        sesion.execute(sql)
