from scripts.weather import get_weather_data
from scripts.checker import check_weather_conditions
from scripts.email_notifier import send_email
from scripts.weather_history import weather_history
from scripts.state import load_state, save_state, get_city_state, should_send_rain_alert, has_rain_stopped, update_city_state
from scripts.logger import setup_logger, get_logger
import os
from dotenv import load_dotenv
import pandas as pd
import sys

load_dotenv()
setup_logger()
logger = get_logger()

API_KEY = os.getenv("WEATHER_API_KEY")
DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "weather_locations.csv")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
ADVERSE_CONDITIONS = ["Rain", "Drizzle", "Thunderstorm"]

def load_locations():
    """
    Read weather_locations.csv, exit if the file not exist

    returns:
        Dataframe: locations data
    """

    if not os.path.exists(CSV_PATH):
        logger.error(f"Locations file not found: {CSV_PATH}. Run get_locations_lat_lon.py first.")
        sys.exit(1)

    locations = pd.read_csv(CSV_PATH)
    logger.info(f"Loaded {len(locations)} location(s) from {CSV_PATH}.")

    return locations

def process_alerts(weather_data: list, state: dict):
    """
    
    """

    to_notify_started = []
    to_notify_stopped = []

    for data in weather_data:
        city = data['location']
        city_state = get_city_state(state, city)
        is_raining = data.get("weather_conditions") in ADVERSE_CONDITIONS

        if should_send_rain_alert(city_state, is_raining):
            logger.info(f"Rain started in {city}.")
            to_notify_started.append(data)

        elif has_rain_stopped(city_state, is_raining):
            logger.info(f"Rain stopped in {city}.")
            to_notify_stopped.append(data)

        else:
            logger.info(f"No state change for {city}, skipping notification.")

        # Update state for this city
        state = update_city_state(state, city, is_raining)

    return to_notify_started, to_notify_stopped, state

def run():
    locations = load_locations
    state = load_state

    weather_data = get_weather_data(locations, API_KEY, BASE_URL)
    weather_history(weather_data)

    if not weather_data:
        logger.warning("No weather data returned, skipping checks.")
        save_state(state)
        return
    
    is_any_adverse, matched = check_weather_conditions(weather_data)

    to_notify_started, to_notify_stopped, state = process_alerts(weather_data, state)

    if to_notify_started:
        logger.info(f"Sending rain started alert for {len(to_notify_started)} location(s).")
        send_email(to_notify_started, subject="🌧️ Rain Alert — Rain Started")

    if to_notify_stopped:
        logger.info(f"Sending rain stopped alert for {len(to_notify_stopped)} location(s).")
        send_email(to_notify_stopped, subject="☀️ Rain Stopped — Rain Stopped")

    save_state(state)

    logger.info("Weather check completed.")