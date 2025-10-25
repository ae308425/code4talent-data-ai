import requests 
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s', filename="ingest.log",filemode="a",encoding="utf-8")

def get_weather_data():
    url = f"https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)
    if response.status_code == 200:
        logging.info("Se obtuvo datos de la API")
        return response.json()
    else:
        logging.error("No se obtuvo datos de la API")
        return