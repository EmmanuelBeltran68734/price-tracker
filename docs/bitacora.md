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


---

## Semana 1 — Crawler (Issue #3)

### Revisión de robots.txt (30 oct 2026)
| Tienda | Páginas de producto | Rutas prohibidas relevantes | Crawl-delay | Notas |
|---|---|---|---|---|
| Alkosto | ✅ Permitidas (`/p/`) | búsquedas (`?q=`, `/search/`), carrito, checkout, cuenta | No tiene | Tiene `sitemap-productos.xml` |
| Éxito | ✅ Permitidas (`/p`) | `/api/`, búsqueda (`/s?`), checkout, cuenta, facetas | No tiene | Cloudflare: `search=yes, ai-train=no` |

**Decisiones:**
- Solo visito páginas de producto que el usuario registra; nunca búsquedas, carrito ni APIs internas.
- Espero entre 2 y 5 segundos entre peticiones e identifico mi bot con un User-Agent propio.
- En Éxito, los `Disallow` quedaron técnicamente bajo `User-agent: Applebot-Extended`, pero respeto su intención y los aplico a mi bot.
- Si una tienda bloquea el bot (por ejemplo, con un desafío de Cloudflare), no intento saltarme la protección: la descarto.

### Exploración con httpx (30 oct 2026)
- **Alkosto** respondió 200. Su JSON-LD solo trae `BreadcrumbList`; el precio está en **microdata** (`<meta itemprop="price" content="2999000.0">`).
- **Éxito** respondio 404 con un producto de marketplace (`-mp`) que ya no existía. Con un producto vendido por Éxito respondio 200 y su **JSON-LD** trae `@type: Product` con `offers.price = 3299900`.
- **Aprendizaje:** explorar antes de programar. Asumí que todas las tiendas usaban JSON-LD y no era así -> el extractor soportará JSON-LD **y** microdata (patrón Strategy).
- No fue necesario cambiar el User-Agent: el bot se identifica honestamente y ambas tiendas responden.
- `normalizar_precio` rechaza precios ≤ 0: un $0 (producto agotado) generaría alertas falsas. "1.500" se interpreta como mil quinientos (correcto en COP).


### Extractores con patrón Strategy (31 oct – 10 nov 2026)
- Clase base abstracta `Extractor` con un solo método: `extraer(html) -> ProductoExtraido`.
- `JsonLdExtractor` (Éxito) y `MicrodataExtractor` (Alkosto) cumplen ese mismo molde.
- `elegir_extractor(url)` escoge la estrategia según el dominio con un diccionario: agregar una tienda nueva es **una línea**.

**Trampas que encontré en el HTML de Alkosto:**
1. **Dos `itemprop="name"`:** el del producto y el de la marca ("PLAYSTATION"), que está anidado. → Solo tomo propiedades cuyo `itemscope` más cercano es el producto.
2. **URL de imagen duplicada:** `https://www.alkosto.comhttps://cdn...` (error de la tienda). → Me quedo con la parte desde el último `https://`.

**Decisiones:**
| Decisión | Por qué |
|---|---|
| Comparar el dominio **exacto** (`exito.com`), no `"exito.com" in url` | `exito.com.falso.co` contiene el texto pero es otro sitio (seguridad). |
| Precio como `Decimal`, nunca `float` | `float` tiene errores de redondeo con dinero. |
| Tests con **fixtures** (páginas guardadas en `tests/fixtures/`) | Funcionan sin internet, dan siempre el mismo resultado y no hacen peticiones a las tiendas en cada push. |

**Problemas:**
- `test_extractores.py` vacío (0 bytes) → no lo había guardado.
- `No module named 'app'` → corrí pytest desde la raíz y no desde `backend/`, donde está `pyproject.toml`.

### Base de datos (11 – 17 nov 2026)
- Configuración con **pydantic-settings**: `DATABASE_URL` se lee del `.env`, nunca va escrita en el código.
- 4 tablas con **SQLAlchemy**: `tiendas`, `productos`, `historial_precios` y `ejecuciones_crawler`.
- **Alembic** para las migraciones ("Git para la base de datos"), con hooks que pasan ruff a cada migración generada.
- `normalizar_url` (sin `?utm_...` ni `#`) + URL única → el mismo producto nunca se guarda dos veces.
- `guardar_precio` con el patrón **obtener o crear** y **unidad de trabajo** (un solo `commit` al final).

**Problemas y cómo los resolví:**
1. **Contraseña real en `.env.example`** (archivo público en GitHub). → La cambié por `cambia_esta_clave` y **cambié la contraseña** de la base de datos: borrarla del archivo no basta, porque queda en el historial de Git.
2. **"la autentificación password falló" en español:** había **dos Postgres** en el puerto 5432 (uno instalado en Windows y el de Docker). → Moví el de Docker al **5433**. La pista fue el idioma: el de Docker responde en inglés.
3. **Docker seguía usando la contraseña vieja:** VS Code cargaba el `.env` viejo en la terminal (`python.terminal.useEnvFile`) y una variable de la terminal **le gana** al archivo `.env`. → Desactivé la opción y recargué VS Code.
4. **`postgressql`** (doble s) en la URL. → Se escribe `postgresql`.

### Crawler en vivo (18 nov 2026)
- `descargar` reintenta solo errores **temporales** (429, 5xx, red) con **espera exponencial** (2 s, 4 s); un 404 o 403 no se reintenta.
- Tests sin internet ni esperas reales gracias a `httpx.MockTransport` y un reloj falso (**inyección de dependencias**).
- El crawler guarda cada ejecución en `ejecuciones_crawler`; si un producto falla, lo anota y sigue con los demás.
- **Primera ejecución real:** Alkosto respondió 200 ✅. **Éxito respondió 403 (Prohibido)**: ahora bloquea al bot.
  → **Decisión:** respeto el bloqueo. No me hago pasar por un navegador ni evado su protección. Conservo el extractor JSON-LD y sus tests; la segunda fuente en vivo será **Mercado Libre por su API oficial** (Semana 3).

### Resumen de la Semana 1
- **56 tests** en verde, sin depender de internet ni de Postgres (fixtures + SQLite en memoria).
- **Aprendizajes:** TDD (rojo → verde → refactor), patrón Strategy, `Decimal` para dinero, migraciones, logs con niveles y que un buen crawler sabe **cuándo no insistir**.
