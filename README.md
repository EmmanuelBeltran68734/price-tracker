# Price Tracker

Plataforma que vigila precios de productos en tiendas en línea de Colombia, guarda su historial y avisa por Telegram cuando un producto baja del precio objetivo.

## Estado

🚧 En construcción - Semana 0 (preparación del entorno).

## Stack planeado

- **Crawler:** Python 3.12, httpx, BeautifulSoup
- **API:** FastAPI, SQLAlchemy, Alembic, JWT
- **Base de datos:** PostgreSQL
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Infraestructura:** Docker Compose, GitHub Actions

## Crawling responsable

Este proyecto respeta el archivo `robots.txt` y los términos de uso de cada tienda, limita la frecuencia de las peticiones y no recolecta datos personales.