import sqlite3
import json
from ingest import get_weather_data

con = sqlite3.connect('weather.db')

with open('init.sql') as f:
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
con.close()