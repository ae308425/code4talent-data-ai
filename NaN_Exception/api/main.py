from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import psycopg2
from decimal import Decimal
from datetime import datetime
from api.websocket_conn import router as ws_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.include_router(ws_router)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")


app.mount("/static", StaticFiles(directory=static_dir), name="static")

origins = [
    "http://localhost:3000",  
    "http://127.0.0.1:3000",  
    "http://localhost:8000", 
    "*"             
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,          
    allow_methods=["*"],             
    allow_headers=["*"],
)

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "climate_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "administrator")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hackathon2025")

def get_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

def safe_convert(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value

@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/series")
async def get_latest_records():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                    latitude, 
                    longitude, 
                    date, 
                    hour,
                    avg_temperature, 
                    avg_relative_humidity,
                    avg_wind_speed, 
                    avg_cloud_cover, 
                    mm_temp
                    FROM weather_data_view
                    ORDER BY timestamp DESC;
                """)
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

                data = [
                    {col: safe_convert(val) for col, val in zip(columns, row)}
                    for row in rows
                ]

        return JSONResponse(content={"count": len(data), "records": data})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
app.include_router(ws_router)

    