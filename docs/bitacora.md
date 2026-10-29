# Bitácora del proyecto

Registro de decisiones, problemas y soluciones. Me sirve para el README y para contar el proyecto en entrevistas (método STAR).

---

## Semana 0 — Preparación (27–28 oct 2026)

### Qué hice
- Instalé Docker Desktop (con WSL 2) y Node.js LTS.
- Creé el repositorio `price-tracker` en GitHub con la CLI `gh`.
- Configuré el backend con **uv** y Python 3.12, aunque mi PC tiene 3.14.
- Levanté PostgreSQL 17 con Docker Compose.
- Agregué CI con GitHub Actions (ruff + pytest) e hice mi primer Pull Request (#1).
- Creé los Issues de cada semana (#2 a #7) y un tablero en GitHub Projects.

### Decisiones
| Decisión | Por qué |
|---|---|
| Python 3.12 con uv en vez de 3.14 | Compatibilidad de librerías; uv instala la versión solo para el proyecto. |
| PostgreSQL en Docker | No ensucia Windows y luego todo el proyecto corre con `docker compose up`. |
| `.env` fuera de Git y `.env.example` dentro | Los secretos no se publican, pero otros saben qué variables configurar. |
| Ramas + Pull Requests aunque trabajo sola | Practicar el flujo profesional; el CI revisa cada cambio antes de llegar a `main`. |

### Problemas y cómo los resolví
1. **Archivos vacíos (0 bytes):** pegaba el código pero no guardaba. → Activé *Auto Save* en VS Code.
2. **`tests` creado como archivo y no como carpeta:** pytest no encontraba los tests. → Lo borré y creé `tests/test_smoke.py` con la barra.
3. **`services must be a mapping` en Docker Compose:** la indentación del YAML estaba mal. → En YAML los espacios definen qué va dentro de qué.
4. **`failed to connect to the docker API`:** Docker Desktop estaba cerrado. → El comando `docker` necesita el motor encendido.
5. **ruff `E501 Line too long`:** una línea del test tenía 111 caracteres. → `uv run ruff format .` la arregló solo.

### Qué aprendí
- La diferencia entre Git (historial local) y GitHub (copia en la nube).
- Qué es un entorno virtual y por qué `uv.lock` sí se sube pero `.venv` no.
- Qué es CI y cómo `Closes #N` conecta un PR con un Issue.