import sqlite3
import json
import os
from ingest import get_weather_data
import logging

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "weather.db")
SQL_PATH = os.path.join(BASE_DIR,  "init.sql")

logging.info("Conectando a base de datos")

con = sqlite3.connect(DB_PATH)

with open(SQL_PATH) as f:
    con.executescript(f.read())

cur = con.cursor()

data = get_weather_data()

## Variables to insert the data in weather_obs
source = "open-meteo"
lat = data["latitude"]
lon = data["longitude"]


obs_time = data["hourly"]["time"] 
temperature = data["hourly"]["temperature_2m"]
humidity = data["hourly"]["relative_humidity_2m"]
logging.info(f"Se va a insertar {len(temperature)} registros")

for record in range(len(obs_time)):
    cur.execute("""
        INSERT OR REPLACE INTO weather_obs (obs_time, lat, lon, source, temperature, humidity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        obs_time[record],
        lat,
        lon,
        source,
        temperature[record],
        humidity[record]
    ))


con.commit()
logging.info("Los datos fueron insertados corrrectamente")
con.close()