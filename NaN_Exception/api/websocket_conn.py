from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import psycopg2
import os
from decimal import Decimal
from datetime import datetime
import traceback

router = APIRouter()

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

active_conn = []

@router.websocket("/ws/weather")
async def weather_ws(websocket: WebSocket):
    await websocket.accept()
    active_conn.append(websocket)
    print("Conexion aceptada por Websocket")
    
    try:
        while True:
            await asyncio.sleep(5)
            
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                                SELECT
                                LATITUDE,
                                LONGITUDE,
                                TEMPERATURE,
                                RELATIVE_HUMIDITY, 
                                WIND_SPEED, 
                                CLOUD_COVER,
                                TIMESTAMP
                                FROM weather_data
                                ORDER BY timestamp DESC;
                                """)
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    data = [
                        {col: safe_convert(val) for col, val in zip(columns, row)}
                        for row in rows
                    ]
            print(f"📦 Enviando {len(data)} registros")
            await websocket.send_json({"ultimo_registro":data})
            

    
    except WebSocketDisconnect:
        print("Websocket desconectado")
        active_conn.remove(websocket)
    except Exception as e:
        print("❌ Error en WebSocket:")
        traceback.print_exc()
        await websocket.close()
    