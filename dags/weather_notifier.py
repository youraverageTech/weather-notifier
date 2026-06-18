from airflow.sdk import dag, task
import os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta
import pandas as pd
from include.logger import setup_logger, get_logger
import pendulum


load_dotenv()
setup_logger()
logger = get_logger()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
ADVERSE_CONDITIONS = ["Rain", "Drizzle", "Thunderstorm"]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "include", "data", "weather_locations.csv")


@dag(
    dag_id = "Weather_Notifier_Pipeline",
    start_date = pendulum.datetime(2026, 6, 1, tz="Asia/Jakarta"),
    schedule = timedelta(minutes=10),
    catchup = False,
    default_args = {
        "retries": 1,
        "retry_delay": timedelta(minutes=5)
    },
    max_active_runs = 1
)
def weather_pipeline():
    @task()
    def load_locations():
        if not os.path.exists(CSV_PATH):
            logger.error(f"Locations file not found: {CSV_PATH}. Run get_locations_lat_lon.py first.")
            raise FileNotFoundError(f"Locations file not found: {CSV_PATH}. Run get_locations_lat_lon.py first.")
        
        locations = pd.read_csv(CSV_PATH)
        logger.info(f"Loaded {len(locations)} location(s) from {CSV_PATH}.")

        return locations
    
    @task()
    def fetch_weather_data(locations):
        from include.weather import get_weather_data
        weather_data = get_weather_data(locations, API_KEY, BASE_URL)

        if not weather_data:
            logger.error("No weather data returned")
            raise ValueError("No weather data returned")
        
        return weather_data
    
    @task()
    def load_weather_history(weather_data):
        from include.weather_history import init_table, save_weather_history
        init_table()
        save_weather_history(weather_data)
    
    @task()
    def check_and_notify_alerts(weather_data):
        from include.state import init_state_table, get_city_state, should_send_rain_alert, has_rain_stopped, update_city_state

        # initialize state table
        init_state_table()

        if not weather_data:
            logger.error("No weather data returned")
            raise ValueError("No weather data returned")

        to_notify_started = []
        to_notify_stopped = []

        for data in weather_data:
            city = data['location']
            city_state = get_city_state(city)
            is_raining = data.get("weather_conditions") in ADVERSE_CONDITIONS # Checking the weather condition
            
            alert_triggered = False

            if should_send_rain_alert(city_state, is_raining):
                logger.info(f"Rain started in {city}.")
                to_notify_started.append(data)
                alert_triggered = True

            elif has_rain_stopped(city_state, is_raining):
                logger.info(f"Rain stopped in {city}.")
                to_notify_stopped.append(data)
                alert_triggered = True

            else:
                logger.info(f"No state change for {city}, skipping notification.")

            # Update state for this city
            update_city_state(city, is_raining, alert_sent=alert_triggered)

        return {
            "to_notify_started": to_notify_started,
            "to_notify_stopped": to_notify_stopped
        }

    @task.branch()
    def check_conditions(notify_data):
        if notify_data['to_notify_started'] or notify_data['to_notify_stopped']:
            return "sending_alerts"
        else:
            return "end_pipeline"

    @task()
    def sending_alerts(notify_data):
        from include.email_notifier import send_email
        if notify_data['to_notify_started']:
            logger.info(f"Sending rain started alert for {len(notify_data['to_notify_started'])} location(s).")
            send_email(notify_data['to_notify_started'], subject="🌧️ Rain Alert — Rain Started")

        if notify_data['to_notify_stopped']:
            logger.info(f"Sending rain stopped alert for {len(notify_data['to_notify_stopped'])} location(s).")
            send_email(notify_data['to_notify_stopped'], subject="☀️ Rain Stopped — Rain Stopped")

    @task()
    def end_pipeline():
        logger.info("Pipeline run successfully")


    locations = load_locations()
    weather_data = fetch_weather_data(locations)
    load_weather_history(weather_data)
    notify_data = check_and_notify_alerts(weather_data)
    checks_branch = check_conditions(notify_data)
    checks_branch >> [sending_alerts(notify_data), end_pipeline()]

weather_pipeline()
