import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")
locations = {
    "Jakarta Barat": [-6.1683, 106.7588],
    "Jakarta Pusat": [-6.1777, 106.8403],
    "Jakarta Selatan": [-6.2838, 106.8049],
    "Jakarta Timur": [-6.2250, 106.9004],
    "Jakarta Utara": [-6.1451, 106.8995],
}

base_url = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_data(locations: dict):
    weather_data = {}
    for location, coords in locations.items():
        params = {
            "lat": coords[0],
            "lon": coords[1],
            "appid": api_key,
            "units": "metric",
        }
        response = requests.get(base_url, params=params)
        try:
            if response.status_code == 200:
                data = response.json()
                weather_desc = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                weather_data[location] = {
                    "description": weather_desc,
                    "temperature": temp,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "location": data["name"]
                }
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred for {location}: {http_err}")
    
    return weather_data

if __name__ == "__main__":
    weather_info = get_weather_data(locations)
    for location, data in weather_info.items():
        print(f"{data['location']}: {data['description']}, Temp: {data['temperature']}°C, Humidity: {data['humidity']}%, Wind Speed: {data['wind_speed']} m/s")
            
        
