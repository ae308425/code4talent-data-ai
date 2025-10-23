import requests
import time
import logging
from datetime import datetime

url = "https://api.open-meteo.com/v1/forecast?latitude=-0.2298&longitude=-78.525&current=temperature_2m,relative_humidity_2m,wind_speed_10m,cloud_cover&timezone=America%2FNew_York&forecast_days=1"

logging.basicConfig(level=logging.INFO)

def data_call():
        try:
            response = requests.get(url)
            data = response.json()

            information_column = {key: data[key] for key in ['latitude', 'longitude']}
            values_column = {key: data['current'][key] for key in ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m', 'cloud_cover']}

            appended_columns = {**information_column, **values_column, "timestamp": datetime.now().isoformat()}
            print(appended_columns)
            return appended_columns
        
        except Exception as e:
            logging.error(f"API call failed: {e}")
            return None