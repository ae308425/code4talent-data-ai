DROP TABLE IF EXISTS weather_obs;

CREATE TABLE weather_obs (
  obs_time TIMESTAMP PRIMARY KEY,
  lat REAL,
  lon REAL,
  source TEXT,
  temperature REAL,
  humidity REAL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);