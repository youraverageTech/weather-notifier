"""
Weather history module for the weather notifier application.

This module handles storing and managing historical weather data by appending
weather records to a postgres database. It provides functionality to save weather data
in a persistent format for later analysis and tracking.
"""

from airflow.providers.postgres.hooks.postgres import PostgresHook
from include.logger import setup_logger, get_logger

setup_logger()
logger = get_logger()

def init_table() -> None:
    hook = PostgresHook(postgres_conn_id= "weather_db_conn")
    
    with hook.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_history (
                id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                location            TEXT NOT NULL,
                weather_conditions  TEXT NOT NULL,
                description         TEXT,
                temperature         FLOAT,
                humidity            INTEGER,
                wind_speed          REAL,
                date                DATE,
                time                TIME
            )    
        """)
        conn.commit()
        logger.info("Table weather_history created successfully.")

def save_weather_history(weather_data: list) -> None:
    if not weather_data:
        logger.warning("No weather data to save.")
        return

    hook = PostgresHook(postgres_conn_id= "weather_db_conn")

    rows = [(
        data['location'],
        data['weather_conditions'],
        data['description'],
        data['temperature'],
        data['humidity'],
        data['wind_speed'],
        data['date'],
        data['time']
    ) for data in weather_data]

    with hook.get_conn() as conn:
        cursor = conn.cursor()

        cursor.executemany("""
            INSERT INTO weather_history (
                location,
                weather_conditions,
                description,
                temperature,
                humidity,
                wind_speed,
                date,
                time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, rows)
        conn.commit()
        logger.info(f"Saved {len(rows)} record(s) to database.")

