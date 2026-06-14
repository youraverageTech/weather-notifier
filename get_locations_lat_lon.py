import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")
locations = ["Jakarta Barat", "Jakarta Pusat", "Jakarta Selatan", "Jakarta Timur", "Jakarta Utara"]
base_url = "https://api.openweathermap.org/geo/1.0/direct"

def get_coordinates(locations):
    weather_locations = []
    for location in locations:
        params = {
            "q": location,
            "limit": 1,
            "appid": api_key
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            try:
                data = response.json()
                if data:
                    lat = data[0]['lat']
                    lon = data[0]['lon']
                    loc = data[0]['local_names']['id']
                    weather_locations.append({
                        'name': loc,
                        'latitude': lat,
                        'longitude': lon
                    })
            except requests.HTTPError as http_err:
                print(f"HTTP error occurred for {location}: {http_err}")
    
    df = pd.DataFrame(weather_locations)
    print(df)
    df.to_csv('weather_locations.csv', index=False)
    
    return weather_locations
if __name__ == "__main__":
    get_coordinates(locations)