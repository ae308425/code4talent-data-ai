# 🌦️ Code 4 Talent | Data & AI — Weather Data Pipeline MVP

## 🧭 Descripción General

Este proyecto implementa un flujo completo (**end-to-end**) de procesamiento de datos meteorológicos, que abarca desde la **ingesta de datos** hasta la **visualización en tiempo real**.  

El MVP busca simular un sistema productivo moderno de *data pipeline*, aplicando conceptos de ingeniería de datos, APIs y detección de anomalías.

---

## 🎯 Objetivo del Entregable (MVP)

El sistema debe cumplir los siguientes objetivos:

- Obtener datos meteorológicos desde la API pública de **[Open-Meteo](https://open-meteo.com)** o desde fuentes simuladas.
- Publicar y transportar los eventos mediante una **cola o canal de mensajería** (Kafka, Redis Pub/Sub o una cola local).
- Normalizar y almacenar los datos en una **base de datos relacional** (PostgreSQL o SQLite).
- Exponer una **API REST** y un **WebSocket** que proporcionen:
  - Series históricas de observaciones.
  - Detección simple de anomalías (±3σ).
  - Predicción básica (último valor o media móvil).
- Incluir una **interfaz web ligera** que consuma el WebSocket y visualice los resultados en tiempo real.

El alcance mínimo consiste en scripts o servicios ligeros que cumplan cada rol.  
Los módulos pueden ejecutarse en una misma máquina o como procesos independientes.

---

## ⚙️ Tecnologías Recomendadas

| Componente | Tecnología sugerida |
|-------------|--------------------|
| Lenguaje | Python 3.10+ |
| Framework Web | FastAPI + Uvicorn |
| Transporte de mensajes | Kafka (opcional), Redis Pub/Sub o cola en memoria |
| Base de datos | PostgreSQL (recomendada) o SQLite |
| Frontend | HTML + JavaScript (WebSocket + REST) |
| Entorno virtual | Virtualenv o Poetry |

---

## 🔧 Requerimientos Funcionales

### 🛰️ Ingesta
- Script que consulta la API de Open-Meteo o una fuente simulada.
- Publica eventos JSON cada *X* segundos en un canal o cola.

**Ejemplo de evento JSON:**
```json
{
  "obs_time": "2025-10-20T12:00:00Z",
  "lat": 40.4168,
  "lon": -3.7038,
  "source": "open-meteo",
  "temperature": 18.5,
  "humidity": 56
}
```

---

### 🧮 Procesamiento
- Un consumidor que toma los eventos, los normaliza y realiza un **upsert** en la base de datos.  
- Garantiza tipos válidos y timestamps consistentes.

**Esquema base SQL:**
```sql
CREATE TABLE IF NOT EXISTS weather_obs (
  obs_time TIMESTAMP PRIMARY KEY,
  lat REAL,
  lon REAL,
  source TEXT,
  temperature REAL,
  humidity REAL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 🧠 Inferencia y API

Endpoints REST expuestos a través de **FastAPI**:

| Método | Endpoint | Descripción |
|---------|-----------|-------------|
| GET | `/series?lat=&lon=&source=&limit=50` | Devuelve las últimas N observaciones. |
| GET | `/anomaly/latest?lat=&lon=&source=` | Detecta si la última observación es una anomalía (±3σ). |
| GET | `/predict/next?lat=&lon=&source=` | Realiza una predicción simple (último valor o media móvil). |

**WebSocket:**  
`/ws` — Envía cada 5 segundos el último registro y su estado (anómalo o normal).

---

## 🚫 Requerimientos No Funcionales

- Tiempo estimado total de desarrollo: **4 horas**.
- Ejecución local en entorno virtual.
- Documentación mínima en `README.md` con instrucciones claras.
- Logs básicos y manejo de errores (con reintento en ingest).
- Compatible con SQLite (modo local) o PostgreSQL.

---

## 🕓 Plan de Trabajo (4 Horas)

| Tiempo | Hito / Tarea |
|--------|---------------|
| 0:00–0:15 | Kickoff, configuración de entorno y roles |
| 0:15–1:15 | Implementar módulo de Ingest (API) |
| 1:15–2:00 | Implementar Processing (consumidor + DB upsert) |
| 2:00–2:30 | Configurar esquema SQL y probar inserciones |
| 2:30–3:15 | Implementar Inference (API REST + WebSocket) |
| 3:15–3:45 | Implementar Frontend y conectar WebSocket |
| 3:45–4:00 | Testing final y empaquetado de entrega |

---

## 🧩 Tareas Opcionales (Stretch Goals)

- Integrar **Kafka** o **Redis** como transporte real.
- Añadir **tests unitarios** para validación de datos y operaciones upsert.
- Implementar **gráfico de anomalías** (por ejemplo, con Chart.js).
- Persistir historial de anomalías y exponer endpoint `/anomalies`.

---

## 📦 Entregables

El repositorio debe contener:

- `ingest.py`  
- `processing.py`  
- `inference/app.py`  
- `index.html`  
- `init.sql` o `weather.db`  
- `README.md` (instrucciones de ejecución)

---

## ▶️ Ejecución Local (Ejemplo)

```bash
# 1. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install fastapi uvicorn requests sqlalchemy psycopg2-binary websockets

# 3. Ejecutar servicios
python ingest.py
python processing.py
uvicorn inference.app:app --reload

# 4. Abrir interfaz
open index.html
```

---

## 🧠 Autores

**Equipo:** Code 4 Talent | Data & AI  
**Propósito:** Ejercicio de integración y flujo de datos en 4 horas (Hackathon / MVP técnico).

---

## 📄 Licencia

MIT License © 2025 Code 4 Talent
