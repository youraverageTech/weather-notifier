from weather import get_weather_data
from checker import check_weather_conditions
from email_notifier import send_email
from weather_history import weather_history
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")
locations_data = pd.read_csv('weather_locations.csv')
base_url = "https://api.openweathermap.org/data/2.5/weather"

if __name__ == "__main__":
    weather_info = get_weather_data(locations_data, api_key, base_url)
    weather_history(weather_info)
    is_checklisted, checklisted_data = check_weather_conditions(weather_info)
    
    if is_checklisted:
        print("Weather conditions match the checklist. Sending notifications...")
        send_email(checklisted_data)
    else:
        print("No weather conditions match the checklist.")