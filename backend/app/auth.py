"""Autenticación básica HTTP de un solo usuario (issue #37).

Stopgap antes de la auth completa por equipo (#34): un único usuario/contraseña
leído de variables de entorno. Sin base de datos, sin librerías nuevas.
"""
import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# Defaults SOLO para desarrollo local. En cualquier entorno desplegado estos
# valores DEBEN venir de variables de entorno reales (AUTH_USER / AUTH_PASSWORD);
# si no, cualquiera entra con admin/changeme. Ver backend/README.md.
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "changeme"


def _expected_credentials() -> tuple[str, str]:
    return (
        os.environ.get("AUTH_USER", DEFAULT_USER),
        os.environ.get("AUTH_PASSWORD", DEFAULT_PASSWORD),
    )


def require_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Valida usuario/contraseña contra AUTH_USER/AUTH_PASSWORD.

    Usa secrets.compare_digest (comparación en tiempo constante) para no filtrar
    por timing si la contraseña es correcta o no. Al fallar, devuelve 401 con la
    cabecera WWW-Authenticate: Basic, que es lo que hace que el navegador muestre
    su popup nativo de login.
    """
    expected_user, expected_password = _expected_credentials()
    user_ok = secrets.compare_digest(credentials.username, expected_user)
    password_ok = secrets.compare_digest(credentials.password, expected_password)
    if not (user_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
