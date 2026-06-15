from scripts.weather import get_weather_data
from scripts.checker import check_weather_conditions
from scripts.email_notifier import send_email
from scripts.weather_history import weather_history
from scripts.state import load_state, save_state, get_city_state, should_send_rain_alert, has_rain_stopped
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")
locations_data = pd.read_csv('weather_locations.csv')
base_url = "https://api.openweathermap.org/data/2.5/weather"

def task_program():
    weather_data = get_weather_data(locations_data, api_key, base_url)
    weather_history(weather_data)
    is_checklisted, checklisted_data = check_weather_conditions(weather_data)
