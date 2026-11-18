# Price Tracker

Plataforma que vigila precios de productos en tiendas en línea de Colombia, guarda su historial y avisa por Telegram cuando un producto baja del precio objetivo.

## Estado

- ✅ **Semana 1:** crawler (Alkosto en vivo; Éxito por JSON-LD), PostgreSQL, migraciones y 56 tests.
- 🚧 **Semana 2:** API con FastAPI y autenticación JWT.

## Cómo ejecutarlo (local)

Requisitos: [Docker Desktop](https://www.docker.com/products/docker-desktop/) y [uv](https://docs.astral.sh/uv/).

1. Copia `.env.example` como `.env` y cambia la contraseña.
2. Levanta la base de datos: `docker compose up -d db`
3. Desde la carpeta `backend`:
   ```bash
   uv sync
   uv run alembic upgrade head
   uv run python -m scripts.guardar_precio_de_prueba   # registra 2 productos de ejemplo
   uv run python -m scripts.ejecutar_crawler           # descarga los precios actuales
   uv run pytest

## Stack planeado

- **Crawler:** Python 3.12, httpx, BeautifulSoup
- **API:** FastAPI, SQLAlchemy, Alembic, JWT
- **Base de datos:** PostgreSQL
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Infraestructura:** Docker Compose, GitHub Actions

## Crawling responsable

Este proyecto respeta el archivo `robots.txt` y los términos de uso de cada tienda, limita la frecuencia de las peticiones y no recolecta datos personales.
