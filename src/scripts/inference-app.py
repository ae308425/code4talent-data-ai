from fastapi import FastAPI
import sqlite3
import os
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s', filename="inference_app.log",filemode="a",encoding="utf-8")

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "weather.db")
SRC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "html"))
app = FastAPI(title = "Weather Inference APP")

app.mount("/static", StaticFiles(directory=SRC_DIR), name="static")


def connect_db(sql, parameters=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute(sql, parameters)
    rows = [dict(row) for row in cursor.fetchall()]
    return rows


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(SRC_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()
    ##return {"message": "Weather Inference API"}

##GET	/series?lat=&lon=&source=&limit=50	Devuelve las últimas N observaciones.
@app.get("/series/")
def get_weather(lat: float = 	52.52, lon: float = 13.419998, source: str = "open-meteo", limit: int = 10):
    logging.info(f"Se recibió GET /series/ request")
    sql = """
        SELECT * FROM weather_obs
        WHERE lat = ? AND lon = ?
        and source = ?
        ORDER BY obs_time DESC
        LIMIT ?;
    """
    data = connect_db(sql, (lat, lon,source, limit))
    logging.info(f"GET /series/ obtuvo {len(data)} filas")
    return {"data": data}

##GET	/anomaly/latest?lat=&lon=&source=	Detecta si la última observación es una anomalía (±3σ).
@app.get("/anomaly/latest/")
def get_anomaly():
        logging.info(f"Se recibió GET /anomaly/latest/ request")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("select * from weather_obs order by obs_time desc limit 1")
        latest_row = cursor.fetchone()
        conn.close()

        if latest_row:
            sql1 = """select * from weather_obs order by obs_time desc limit 100"""
            data = connect_db(sql1 )
            is_anomaly = False
            if len(data)>20:
                logging.info(f"Se usará {len(data)} registros para determinar si es anomalía")
                temperatures = [row["temperature"] for row in data]
                latest_temp = temperatures.pop(0)
                n = len(temperatures)
                mean = sum(temperatures)/n
                variance = sum([(t-mean)**2 for t in temperatures])/(n-1)
                std = variance**0.5
                if latest_temp > (mean+3*std) or latest_temp < (mean-3*std):
                    is_anomaly = True
            else:
                logging.info(f"No hay suficiente información para definir una anomalía")
            data = dict(latest_row)
            data["is_anomaly"] = is_anomaly
            return {"data": data}


##GET	/predict/next?lat=&lon=&source=	Realiza una predicción simple (último valor o media móvil).
@app.get("/predict/next/")
def get_next(lat: float = 	52.52, lon: float = 13.419998, source: str = "open-meteo"):
    logging.info(f"Se recibió GET /predict/next/ request")
    sql = """
        SELECT * FROM weather_obs
        WHERE lat = ? AND lon = ?
        and source = ?
        ORDER BY obs_time DESC
        LIMIT 1;
    """
    data = connect_db(sql, (lat, lon,source))
    logging.info(f"Predicción usando último registro exitosa")
    return {"data":data}