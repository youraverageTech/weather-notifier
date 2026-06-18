"""
State management module for the weather notifier application.

This module handles loading, saving, and updating weather state conditions 
for different cities using PostgreSQL instead of a local JSON file.
"""

from airflow.providers.postgres.hooks.postgres import PostgresHook
from include.logger import setup_logger, get_logger
from datetime import datetime
from zoneinfo import ZoneInfo

setup_logger()
logger = get_logger()

CONN_ID = "weather_db_conn"


def init_state_table() -> None:
    """Create weather_state table if it doesn't exist yet."""
    hook = PostgresHook(postgres_conn_id=CONN_ID)
    with hook.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_state (
                city            TEXT PRIMARY KEY,
                is_raining      BOOLEAN DEFAULT FALSE,
                last_checked    TIMESTAMP,
                alert_sent_at   TIMESTAMP
            )
        """)
        conn.commit()


def get_city_state(city: str) -> dict:
    """
    Retrieve the weather state for a specific city from PostgreSQL.
    Returns default state if city doesn't exist yet.
    """
    hook = PostgresHook(postgres_conn_id=CONN_ID)
    with hook.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT is_raining, last_checked, alert_sent_at
            FROM weather_state
            WHERE city = %s
        """, (city,))
        row = cursor.fetchone()

    if row is None:
        logger.info(f"No existing state for {city}, returning default state.")
        return {
            "is_raining": False,
            "last_checked": None,
            "alert_sent_at": None
        }

    logger.info(f"State found for {city}.")
    return {
        "is_raining": row[0],
        "last_checked": row[1],
        "alert_sent_at": row[2]
    }


def update_city_state(city: str, is_raining: bool, alert_sent: bool = False) -> None:
    """Insert or update the weather state for a specific city."""
    hook = PostgresHook(postgres_conn_id=CONN_ID)
    now = datetime.now(tz=ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")

    with hook.get_conn() as conn:
        cursor = conn.cursor()
        if alert_sent:
            cursor.execute("""
                INSERT INTO weather_state (city, is_raining, last_checked, alert_sent_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (city)
                DO UPDATE SET
                    is_raining = EXCLUDED.is_raining,
                    last_checked = EXCLUDED.last_checked,
                    alert_sent_at = EXCLUDED.alert_sent_at
            """, (city, is_raining, now, now))
            logger.info(f"State updated for {city} - is_raining: {is_raining}, alert sent.")
        else:
            cursor.execute("""
                INSERT INTO weather_state (city, is_raining, last_checked)
                VALUES (%s, %s, %s)
                ON CONFLICT (city)
                DO UPDATE SET
                    is_raining = EXCLUDED.is_raining,
                    last_checked = EXCLUDED.last_checked
            """, (city, is_raining, now))
            logger.info(f"State updated for {city} - is_raining: {is_raining}, no alert.")

        conn.commit()


def should_send_rain_alert(city_state: dict, is_raining: bool) -> bool:
    return is_raining and not city_state["is_raining"]


def has_rain_stopped(city_state: dict, is_raining: bool) -> bool:
    return not is_raining and city_state["is_raining"]