import requests
import os
from dotenv import load_dotenv
import pandas as pd

def get_weather_data(locations: pd.DataFrame, api_key: str, base_url: str) -> list: 
    weather_data = []
    for _, coords in locations.iterrows():
        params = {
            "lat": coords['latitude'],
            "lon": coords['longitude'],
            "appid": api_key,
            "units": "metric",
        }
        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data:
                    weather_desc = data["weather"][0]["description"]
                    temp = data["main"]["temp"]
                    humidity = data["main"]["humidity"]
                    wind_speed = data["wind"]["speed"]
                    weather_conditions = data["weather"][0]["main"]
                    weather_data.append({
                        "location": coords['name'],
                        "description": weather_desc,
                        "temperature": temp,
                        "humidity": humidity,
                        "wind_speed": wind_speed,
                        "weather_conditions": weather_conditions
                    })
                else:
                    print(f"No weather data found for {coords['name']}")
        except requests.RequestException as http_err:
            print(f"HTTP error occurred for {coords['name']}: {http_err}")
    
    return weather_data
        
