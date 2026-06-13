"""
This scripts is to check the weather data from OpenWeatherAPI. 
It will read the weather conditions, if rainy, it will send notification to the user. 
"""

check_conditions = ["Rain", "Drizzle", "Thunderstorm"]

def check_weather_conditions(weather_data):
    checklisted_data = []
    for data in weather_data:
        if data.get("weather_conditions") in check_conditions:
            checklisted_data.append(data)
    return bool(checklisted_data), checklisted_data