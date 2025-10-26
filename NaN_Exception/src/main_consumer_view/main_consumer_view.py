import redis
import psycopg2
import os
from dotenv import load_dotenv
from log_util.logger_config import setup_logger

load_dotenv()

logger = setup_logger(__name__, "main_consumer_view.log")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "climate_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "administrator")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hackathon2025")
REDIS_CHANNEL = "weather_channel"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe(REDIS_CHANNEL)

logger.info("Esperando mensajes...")

try:
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    cur = conn.cursor()
except Exception as e:
    logger.error("Error al conectar con PostgreSQL:", e)
    exit()

for message in pubsub.listen():
    if message["type"] == "message":
        try:
            logger.info(f"Leyendo ultimo mensaje para actualizar vista...")
            cur.execute("""
                SELECT
                LATITUDE, LONGITUDE, TEMPERATURE,
                RELATIVE_HUMIDITY, WIND_SPEED, CLOUD_COVER, TIMESTAMP
                FROM weather_data
                ORDER BY TIMESTAMP DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if not row:
                logger.info("No hay registros en weather_data todavía.")
                continue

            latitude, longitude, temperature, humidity, wind_speed, cloud_cover, ts = row

            query = """
                        INSERT INTO weather_data_view (
                            latitude, longitude, date, hour,
                            avg_temperature, avg_relative_humidity,
                            avg_wind_speed, avg_cloud_cover, mm_temp
                        )
                        SELECT
                            latitude, longitude, date, hour,
                            avg_temperature, avg_relative_humidity,
                            avg_wind_speed, avg_cloud_cover,
                            AVG(avg_temperature) OVER (
                                PARTITION BY latitude, longitude, date
                                ORDER BY hour
                                ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
                            ) AS mm_temp
                        FROM (
                            SELECT
                                latitude,
                                longitude,
                                CAST(timestamp AS DATE) AS date,
                                EXTRACT(HOUR FROM timestamp) AS hour,
                                AVG(temperature) AS avg_temperature,
                                AVG(relative_humidity) AS avg_relative_humidity,
                                AVG(wind_speed) AS avg_wind_speed,
                                AVG(cloud_cover) AS avg_cloud_cover
                            FROM weather_data
                            GROUP BY latitude, longitude, CAST(timestamp AS DATE), EXTRACT(HOUR FROM timestamp)
                        ) AS hourly_data;
                        """

            
            cur.execute(query)
            conn.commit()
            logger.info(f"Registro insertado en weather_data_view con timestamp {ts}\n")

        except Exception as e:
            logger.info("Error al procesar el mensaje:", e)
            conn.rollback()

 